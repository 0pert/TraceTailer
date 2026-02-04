PROFILES = {
    "Standard": [
        {
            "name": "XML Tags",
            "expression": r"</?[A-Za-z_][\w\-\.:]*",
            "color": "#2979FF",
            "enabled": True,
        },
        {
            "name": "Closing Tag",
            "expression": r"/?>",
            "color": "#2979FF",
            "enabled": True,
        },
        {
            "name": "Attributes",
            "expression": r"\b[A-Za-z_][\w\-\.]*(?==)",
            "color": "#F57C00",
            "enabled": True,
        },
        {
            "name": "Quoted Values",
            "expression": r'"[^"]*"',
            "color": "#43A047",
            "enabled": True,
        },
        {
            "name": "Date Time",
            "expression": r"\[\d{2}/\d{2}/\d{2}\s\d{2}:\d{2}:\d{2}\.\d{3}\]",
            "color": "#9C27B0",
            "enabled": True,
        },
        {
            "name": "GUID",
            "expression": r"\{[0-9A-Fa-f-]{36,}\}",
            "color": "#CDDF2E",
            "enabled": True,
        },
        {
            "name": "Error Keywords",
            "expression": r"(?i)\b(?:error|exception|fail|fatal|critical)\b",
            "color": "#E53935",
            "bold": True,
            "enabled": True,
        },
        {
            "name": "Warning Keywords",
            "expression": r"(?i)\b(?:warn|warning|caution)\b",
            "color": "#FF6F00",
            "enabled": True,
        },
        {
            "name": "Success Keywords",
            "expression": r"(?i)\b(?:success|ok|pass|complete)\b",
            "color": "#14F71F",
            "enabled": True,
        },
    ],
    "Profile 2": [
        {
            "name": "XML Tags 2",
            "expression": r"</?[A-Za-z_][\w\-\.:]*",
            "color": "#2979FF",
            "enabled": True,
        },
        {
            "name": "Closing Tag 2",
            "expression": r"/?>",
            "color": "#2979FF",
            "enabled": True,
        },
        {
            "name": "Attributes 2",
            "expression": r"\b[A-Za-z_][\w\-\.]*(?==)",
            "color": "#F57C00",
            "enabled": True,
        },
    ],
    "Profile 3": [
        {
            "name": "XML Tags 3",
            "expression": r"</?[A-Za-z_][\w\-\.:]*",
            "color": "#2979FF",
            "enabled": True,
        },
        {
            "name": "Closing Tag 3",
            "expression": r"/?>",
            "color": "#2979FF",
            "enabled": True,
        },
        {
            "name": "Attributes 3",
            "expression": r"\b[A-Za-z_][\w\-\.]*(?==)",
            "color": "#F57C00",
            "enabled": True,
        },
    ],
}
