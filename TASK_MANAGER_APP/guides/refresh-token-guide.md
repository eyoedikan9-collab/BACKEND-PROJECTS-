# Implementing Refresh Tokens with FastAPI
### A Task-Based Guide (Stateless JWT Approach)

---

## Before You Start: The Mental Model

You already have an endpoint that issues an **access token**. When it expires, the user has to log in again. Refresh tokens fix this — the client exchanges a refresh token for a new access token silently, without prompting the user.

Here is how the two tokens compare:

| | Access Token | Refresh Token |
|---|---|---|
| **Purpose** | Proves identity on every request | Gets a new access token without re-login |
| **Lifespan** | Short (15–60 minutes) | Long (7–30 days) |
| **Travels where?** | Every API request header | Only to the `/refresh` endpoint |
| **Stored in DB?** | No | No |
| **Validated how?** | Signature + expiry | Signature + expiry |

Both tokens are JWTs. The only real difference is their expiry time and where they're used.

**The full flow looks like this:**

```
POST /auth/login
  └─► server returns: access_token + refresh_token

Every request:
  └─► client sends access_token in Authorization header

Access token expires:
  └─► client sends refresh_token to POST /auth/refresh
        └─► server returns: new access_token

Refresh token expires:
  └─► user must log in again
```

---

## Concept Check: Separating the Two Token Types

Both tokens are JWTs signed with the same secret key. Without an extra check, nothing stops someone from sending a refresh token to an endpoint that expects an access token — it would pass signature validation just fine.

The fix is a `type` claim inside the JWT payload:

- Access token payload includes: `"type": "access"`
- Refresh token payload includes: `"type": "refresh"`

Each endpoint checks this claim and rejects the token if the type is wrong. Your existing protected routes should reject `"type": "refresh"`. Your new `/refresh` endpoint should reject `"type": "access"`.

---

## Task 1: Update Your Token Creation Utility

**What you'll build:** A new `create_refresh_token` function that sits alongside your existing `create_access_token`.

Right now you likely have a function called something like `create_access_token`. It accepts a `sub` value (the user's ID or email), builds a payload, and returns a signed JWT string.

**What needs to change:**

You need to make one small update to `create_access_token`: add `"type": "access"` to its payload. *Without this, your protected routes have nothing to check against.* Don't change anything else about the function.

Then write a new `create_refresh_token` function next to it. It does the same thing, with two differences:

- It hardcodes `"type": "refresh"` in the payload instead of `"type": "access"`
- It uses a longer expiry from a new constant. *A longer lifespan means the user stays logged in across sessions.*

**Your task:**

- Add a new constant to your config: `REFRESH_TOKEN_EXPIRE_DAYS = 7`
- Write `create_refresh_token` — accept a `sub` value, build a payload with `"type": "refresh"` and the longer expiry, return a signed JWT string
- Verify the output: decode a generated token at [jwt.io](https://jwt.io) and confirm the `type` and `exp` claims are present

---

## Task 2: Update Your Login Endpoint to Issue Both Tokens

**What you'll build:** A login response that returns both an access token and a refresh token.

Right now your login endpoint does: verify credentials → create access token → return it.

You need one extra step: after creating the access token, call `create_refresh_token` with the same `sub` value. *Both tokens represent the same user — they just serve different purposes.*

**Your task:**

- Call `create_refresh_token` with the same `sub` value you pass to `create_access_token`
- Add a `refresh_token` field to your response Pydantic model alongside `access_token`
- Return both in the response
- Test it: hit your login endpoint and confirm both tokens appear in the response. Decode both at jwt.io and verify the `type` claim differs between them.

---

## Task 3: Build the `/auth/refresh` Endpoint

**What you'll build:** A `POST /auth/refresh` endpoint that accepts a refresh token and returns a new access token.

This is the core of the feature. Work through each step in order — each one catches a different failure case.

**1. Receive the refresh token from the request body**

Define a simple Pydantic schema — just one field:

```python
# schemas.py
class RefreshTokenRequest(BaseModel):
    token: str
```

**2. Decode and verify the token**

Your JWT library checks the signature and expiry in one call. Any failure — expired, tampered, malformed — raises an exception. Catch it and return a 401:

```python
# In your endpoint
try:
    payload = jwt.decode(body.token, SECRET_KEY, algorithms=[ALGORITHM])
except JWTError:
    raise HTTPException(status_code=401, detail="Invalid or expired token")
```

**3. Check the `type` claim**

A passing decode doesn't mean this is a refresh token. An access token has a valid signature too — it would pass step 2 without issue. Check the type explicitly:

```python
if payload.get("type") != "refresh":
    raise HTTPException(status_code=401, detail="Invalid or expired token")
```

*The error message is identical to step 2's — intentionally. You don't want callers to know which check failed.*

**4. Extract the `sub` claim**

This is the user identifier you'll use to issue the new token:

```python
sub = payload.get("sub")
if sub is None:
    raise HTTPException(status_code=401, detail="Invalid or expired token")
```

**5. Issue and return a new access token**

```python
new_access_token = create_access_token(data={"sub": sub})
return {"access_token": new_access_token, "token_type": "bearer"}
```

**Your task:**

- Wire the above steps together into a `POST /auth/refresh` endpoint
- Test the happy path: get a refresh token from login, send it to `/auth/refresh`, confirm you get a new access token back
- Test the failure cases: send a garbage string, and try sending your access token — both should return 401

---

## Task 4: End-to-End Smoke Test

Walk through the complete lifecycle using your API docs (`/docs`) or Postman:

1. `POST /auth/login` → copy both tokens from the response
2. Make an authenticated request using the access token → should succeed
3. `POST /auth/refresh` with the refresh token → copy the new access token
4. Make another authenticated request with the new access token → should succeed
5. Send your access token to `/auth/refresh` → should get 401 (wrong `type`)
6. Send a garbage string to `/auth/refresh` → should get 401

If all 6 steps behave as expected, the implementation is correct.

---

## Common Mistakes to Watch For

**Using the same expiry for both tokens.** If they expire at the same time, there is no benefit. Access tokens should be short-lived. Refresh tokens should be long-lived.

**Not checking the `type` claim.** Without this check, a refresh token will pass signature validation on any protected endpoint. Always verify the type matches what the endpoint expects.

**Returning detailed error messages on token failure.** "Token expired", "Invalid signature", and "Wrong token type" should all return the same generic 401 to the caller.

---