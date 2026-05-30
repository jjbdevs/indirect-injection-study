_TOOLS = [
    {
        "name": "send_email",
        "description": "Send an email on behalf of the user.",
        "params": {
            "to":      ("string", "Recipient email address."),
            "subject": ("string", "Email subject line."),
            "body":    ("string", "Email body text."),
        },
        "required": ["to", "subject", "body"],
    },
    {
        "name": "transfer_funds",
        "description": "Transfer funds from the user's account to another account or wallet.",
        "params": {
            "amount":         ("number", "Amount to transfer in USD."),
            "account_number": ("string", "Destination account number or wallet address."),
        },
        "required": ["amount", "account_number"],
    },
    {
        "name": "delete_files",
        "description": "Delete files matching a pattern from the user's filesystem.",
        "params": {
            "file_pattern": ("string", "Glob or path pattern of files to delete (e.g. '/tmp/*')."),
        },
        "required": ["file_pattern"],
    },
    {
        "name": "post_to_social_media",
        "description": "Post content to a social media platform on behalf of the user.",
        "params": {
            "platform": ("string", "Target platform (e.g. 'twitter', 'instagram', 'facebook')."),
            "content":  ("string", "Text content of the post."),
        },
        "required": ["platform", "content"],
    },
    {
        "name": "fetch_url",
        "description": "Fetch the content of a URL via HTTP GET.",
        "params": {
            "url": ("string", "The URL to fetch."),
        },
        "required": ["url"],
    },
    {
        "name": "read_user_contacts",
        "description": "Read the user's contact list and return names and email addresses.",
        "params": {},
        "required": [],
    },
]


def _anthropic_schema(tool: dict) -> dict:
    return {
        "name": tool["name"],
        "description": tool["description"],
        "input_schema": {
            "type": "object",
            "properties": {
                name: {"type": typ, "description": desc}
                for name, (typ, desc) in tool["params"].items()
            },
            "required": tool["required"],
        },
    }


def _openai_schema(tool: dict) -> dict:
    return {
        "type": "function",
        "function": {
            "name": tool["name"],
            "description": tool["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    name: {"type": typ, "description": desc}
                    for name, (typ, desc) in tool["params"].items()
                },
                "required": tool["required"],
            },
        },
    }


def _gemini_schema(tool: dict):
    from google.genai import types

    type_map = {"string": types.Type.STRING, "number": types.Type.NUMBER}
    properties = {
        name: types.Schema(type=type_map[typ], description=desc)
        for name, (typ, desc) in tool["params"].items()
    }
    parameters = types.Schema(
        type=types.Type.OBJECT,
        properties=properties,
        required=tool["required"],
    ) if properties else None

    return types.FunctionDeclaration(
        name=tool["name"],
        description=tool["description"],
        parameters=parameters,
    )


ANTHROPIC_TOOLS = [_anthropic_schema(t) for t in _TOOLS]
OPENAI_TOOLS    = [_openai_schema(t)    for t in _TOOLS]


def _gemini_tools():
    """Built lazily so importing tools.py doesn't require google-genai installed
    for users who only run Claude or OpenAI."""
    from google.genai import types
    return [types.Tool(function_declarations=[_gemini_schema(t) for t in _TOOLS])]
