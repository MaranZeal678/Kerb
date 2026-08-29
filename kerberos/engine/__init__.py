import os


def mistral_client():
    """SDK-version-tolerant client factory (mistralai 1.x vs 2.x import paths)."""
    try:
        from mistralai.client import Mistral   # 2.x
    except ImportError:
        from mistralai import Mistral          # 1.x
    return Mistral(api_key=os.environ["MISTRAL_API_KEY"])
