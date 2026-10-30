# hello.py

def get_greeting(environment: str = "UAT") -> str:
    """Return a status greeting for the target environment."""
    return f"Hello from MLOps {environment} Environment! Dry Run Successful."


def add_metrics(a: int, b: int) -> int:
    """Simple helper function for pytest verification."""
    return a + b


if __name__ == "__main__":
    print(get_greeting("UAT"))
    print(f"Health Check Calculation (2 + 3): {add_metrics(2, 3)}")
