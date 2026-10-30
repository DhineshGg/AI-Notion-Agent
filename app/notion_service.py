import requests

from config import (
    NOTION_TOKEN,
    NOTION_PARENT_PAGE_ID
)


# ============================================================
# NOTION API CONFIGURATION
# ============================================================

NOTION_API_URL = "https://api.notion.com/v1"

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}


# ============================================================
# INTERNAL REQUEST HELPER
# ============================================================

def _check_response(response, operation):
    """
    Validate a Notion API response.
    """

    if not response.ok:
        raise Exception(
            f"{operation} failed: "
            f"{response.status_code} - {response.text}"
        )

    return response.json()


# ============================================================
# GET PARENT PAGE
# ============================================================

def get_parent_page():
    """
    Retrieve the configured parent/root Notion page.

    This uses NOTION_PARENT_PAGE_ID from config.py.
    """

    if not NOTION_PARENT_PAGE_ID:
        raise ValueError(
            "NOTION_PARENT_PAGE_ID is not configured."
        )

    url = f"{NOTION_API_URL}/pages/{NOTION_PARENT_PAGE_ID}"

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )

    return _check_response(
        response,
        "Getting parent page"
    )


# ============================================================
# GET SPECIFIC NOTION PAGE
# ============================================================

def get_notion_page(page_id):
    """
    Retrieve a specific Notion page using its page ID.

    This function is independent of the configured
    parent page.

    Args:
        page_id (str):
            ID of the Notion page.

    Returns:
        dict:
            Notion page object.
    """

    if not page_id:
        raise ValueError("page_id is required.")

    url = f"{NOTION_API_URL}/pages/{page_id}"

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )

    return _check_response(
        response,
        "Getting Notion page"
    )


# ============================================================
# GET PAGE CONTENT / BLOCKS
# ============================================================

def get_notion_page_content(page_id):
    """
    Retrieve the actual content blocks of a Notion page.

    Args:
        page_id (str):
            ID of the Notion page.

    Returns:
        list:
            List of Notion blocks.
    """

    if not page_id:
        raise ValueError("page_id is required.")

    url = (
        f"{NOTION_API_URL}/blocks/"
        f"{page_id}/children"
    )

    all_blocks = []
    start_cursor = None

    while True:

        params = {
            "page_size": 100
        }

        if start_cursor:
            params["start_cursor"] = start_cursor

        response = requests.get(
            url,
            headers=HEADERS,
            params=params,
            timeout=30
        )

        data = _check_response(
            response,
            "Getting page content"
        )

        all_blocks.extend(
            data.get("results", [])
        )

        if not data.get("has_more"):
            break

        start_cursor = data.get(
            "next_cursor"
        )

        if not start_cursor:
            break

    return all_blocks


# ============================================================
# SEARCH NOTION PAGES
# ============================================================

def search_notion_pages(query=""):
    """
    Search pages accessible to the Notion integration.

    Args:
        query (str):
            Search text.

    Returns:
        list:
            Simplified page information.
    """

    url = f"{NOTION_API_URL}/search"

    payload = {
        "page_size": 100,
        "filter": {
            "property": "object",
            "value": "page"
        }
    }

    if query and query.strip():
        payload["query"] = query.strip()

    response = requests.post(
        url,
        headers=HEADERS,
        json=payload,
        timeout=30
    )

    data = _check_response(
        response,
        "Searching Notion pages"
    )

    pages = []

    for result in data.get("results", []):

        if result.get("object") != "page":
            continue

        page_id = result.get("id")

        properties = result.get(
            "properties",
            {}
        )

        title = "Untitled"

        for property_data in properties.values():

            if property_data.get("type") != "title":
                continue

            title_items = property_data.get(
                "title",
                []
            )

            if title_items:

                title = "".join(
                    item.get("plain_text", "")
                    for item in title_items
                ).strip()

            break

        pages.append({
            "id": page_id,
            "title": title or "Untitled",
            "url": result.get("url", "")
        })

    return pages


# ============================================================
# CREATE NOTION PAGE
# ============================================================

def create_notion_page(
    title,
    content=""
):
    """
    Create a new Notion page under the configured
    parent page.

    Args:
        title (str):
            Page title.

        content (str):
            Optional page content.

    Returns:
        dict:
            Created Notion page.
    """

    if not title or not title.strip():
        raise ValueError(
            "Page title is required."
        )

    title = title.strip()

    url = f"{NOTION_API_URL}/pages"

    payload = {
        "parent": {
            "page_id": NOTION_PARENT_PAGE_ID
        },
        "properties": {
            "title": {
                "title": [
                    {
                        "type": "text",
                        "text": {
                            "content": title
                        }
                    }
                ]
            }
        }
    }

    # --------------------------------------------------------
    # Add page content
    # --------------------------------------------------------

    if content and content.strip():

        payload["children"] = [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": content.strip()
                            }
                        }
                    ]
                }
            }
        ]

    response = requests.post(
        url,
        headers=HEADERS,
        json=payload,
        timeout=30
    )

    return _check_response(
        response,
        "Creating Notion page"
    )


# ============================================================
# EXTRACT TEXT FROM A BLOCK
# ============================================================

def block_to_text(block):
    """
    Convert a Notion block into readable text.
    """

    block_type = block.get("type")

    if not block_type:
        return ""

    block_data = block.get(
        block_type,
        {}
    )

    rich_text = block_data.get(
        "rich_text",
        []
    )

    text = "".join(
        item.get("plain_text", "")
        for item in rich_text
    )

    if block_type == "to_do":

        checked = block_data.get(
            "checked",
            False
        )

        prefix = "[x] " if checked else "[ ] "

        return prefix + text

    if block_type == "bulleted_list_item":
        return f"• {text}"

    if block_type == "numbered_list_item":
        return f"1. {text}"

    if block_type == "heading_1":
        return f"# {text}"

    if block_type == "heading_2":
        return f"## {text}"

    if block_type == "heading_3":
        return f"### {text}"

    if block_type == "quote":
        return f"> {text}"

    if block_type == "code":
        language = block_data.get(
            "language",
            ""
        )

        return (
            f"```{language}\n"
            f"{text}\n"
            f"```"
        )

    if block_type == "divider":
        return "---"

    return text


# ============================================================
# GET READABLE PAGE CONTENT
# ============================================================

def get_readable_page_content(page_id):
    """
    Retrieve a page and convert its blocks into readable text.
    """

    page = get_notion_page(page_id)

    blocks = get_notion_page_content(
        page_id
    )

    title = "Untitled"

    properties = page.get(
        "properties",
        {}
    )

    for property_data in properties.values():

        if property_data.get("type") != "title":
            continue

        title_items = property_data.get(
            "title",
            []
        )

        if title_items:
            title = "".join(
                item.get("plain_text", "")
                for item in title_items
            ).strip()

        break

    content_lines = []

    for block in blocks:

        text = block_to_text(block)

        if text.strip():
            content_lines.append(text)

    return {
        "id": page_id,
        "title": title,
        "url": page.get("url", ""),
        "content": "\n\n".join(
            content_lines
        )
    }