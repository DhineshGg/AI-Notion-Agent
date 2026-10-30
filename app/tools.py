from langchain.tools import tool

from notion_service import (
    create_notion_page,
    search_notion_pages,
    get_notion_page,
    get_notion_page_content,
    get_readable_page_content
)


# ============================================================
# CREATE PAGE TOOL
# ============================================================

@tool
def create_page(
    title: str,
    content: str = ""
) -> str:
    """
    Create a new page in the user's Notion workspace.

    Use this when the user wants to create a new
    Notion page.
    """

    result = create_notion_page(
        title=title,
        content=content
    )

    page_id = result.get(
        "id",
        "unknown"
    )

    page_url = result.get(
        "url",
        ""
    )

    return (
        f"Page created successfully.\n"
        f"Title: {title}\n"
        f"Page ID: {page_id}\n"
        f"URL: {page_url}"
    )


# ============================================================
# SEARCH PAGES TOOL
# ============================================================

@tool
def search_pages(query: str) -> str:
    """
    Search the user's Notion pages.

    Use this when the user wants to find pages
    matching a title or topic.
    """

    results = search_notion_pages(
        query=query
    )

    if not results:
        return (
            f"No Notion pages found for "
            f"'{query}'."
        )

    lines = [
        f"Found {len(results)} page(s):"
    ]

    for index, page in enumerate(
        results,
        start=1
    ):

        lines.append(
            f"{index}. {page['title']}\n"
            f"   ID: {page['id']}\n"
            f"   URL: {page.get('url', '')}"
        )

    return "\n".join(lines)


# ============================================================
# GET PAGE TOOL
# ============================================================

@tool
def get_page(page_id: str) -> str:
    """
    Retrieve metadata for one specific Notion page
    using its page ID.

    This is an internal operation. The user normally
    does not need to know the page ID.
    """

    page = get_notion_page(
        page_id
    )

    return (
        f"Page retrieved successfully.\n"
        f"ID: {page.get('id', '')}\n"
        f"URL: {page.get('url', '')}\n"
        f"Created: {page.get('created_time', '')}\n"
        f"Last edited: {page.get('last_edited_time', '')}"
    )


# ============================================================
# GET PAGE CONTENT TOOL
# ============================================================

@tool
def get_page_content(page_id: str) -> str:
    """
    Retrieve the actual readable content of a specific
    Notion page using its page ID.
    """

    result = get_readable_page_content(
        page_id
    )

    return (
        f"Page: {result['title']}\n"
        f"Page ID: {result['id']}\n"
        f"URL: {result['url']}\n\n"
        f"{result['content']}"
    )


# ============================================================
# READ PAGE BY NAME / DESCRIPTION
# ============================================================

@tool
def read_page(query: str) -> str:
    """
    Find a Notion page based on the user's description
    and read its content.

    The user does NOT need to provide a page ID.

    Example:
        'Read my machine learning project page'
    """

    results = search_notion_pages(
        query=query
    )

    if not results:
        return (
            f"I couldn't find a Notion page "
            f"matching '{query}'."
        )

    # Use the first matching page.
    page = results[0]

    page_id = page["id"]

    readable = get_readable_page_content(
        page_id
    )

    return (
        f"Page: {readable['title']}\n"
        f"URL: {readable['url']}\n\n"
        f"{readable['content']}"
    )


# ============================================================
# TOOL LIST
# ============================================================

tools = [
    create_page,
    search_pages,
    get_page,
    get_page_content,
    read_page
]