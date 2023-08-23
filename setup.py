import os

if os.getenv("ENV"):
    with open(".env", "w") as f:
        f.write(os.environ["ENV"])
    print("Written .env file from ENV")

print("Setup complete.")