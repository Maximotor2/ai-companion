from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request

_BRAVE_API_URL = "https://api.search.brave.com/res/v1/web/search"
_MAX_RESULTS = 5


def brave_search(query: str, num_results: int = _MAX_RESULTS) -> str:
    """
    Call the Brave Search API and return a formatted results block.

    Returns a human-readable string suitable for embedding in a prompt.
    Raises ValueError if BRAVE_API_KEY is not set.
    Raises RuntimeError on HTTP/network errors.
    """
    api_key = os.getenv("BRAVE_API_KEY")
    if not api_key:
        raise ValueError(
            "BRAVE_API_KEY is not set. "
            "Add it as a Windows environment variable or in your .env file."
        )

    params = urllib.parse.urlencode({
        "q": query,
        "count": min(num_results, 20),
        "safesearch": "moderate",
    })
    url = f"{_BRAVE_API_URL}?{params}"

    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": api_key,
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read()
            # urllib handles gzip transparently when Accept-Encoding is set
            data = json.loads(raw)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Brave Search HTTP {e.code}: {body}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Brave Search network error: {e.reason}") from e

    results = data.get("web", {}).get("results", [])
    if not results:
        return "No results found."

    lines: list[str] = []
    for i, r in enumerate(results[:num_results], 1):
        title = r.get("title", "(no title)")
        url_r = r.get("url", "")
        desc = (r.get("description") or "").strip()
        lines.append(f"{i}. {title}")
        if url_r:
            lines.append(f"   URL: {url_r}")
        if desc:
            lines.append(f"   {desc}")

    return "\n".join(lines)
