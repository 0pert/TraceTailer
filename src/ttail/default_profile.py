DEFAULT_PROFILE = """{
  "Default": [
    {
      "name": "XML Tags",
      "expression": "</?[A-Za-z_][\\\\w\\\\-\\\\.:]*",
      "color": "#2979FF",
      "enabled": true
    },
    {
      "name": "Closing Tag",
      "expression": "/?>",
      "color": "#2979FF",
      "enabled": true
    },
    {
      "name": "Attributes",
      "expression": "\\\\b[A-Za-z_][\\\\w\\\\-\\\\.]*(?==)",
      "color": "#F57C00",
      "enabled": true
    },
    {
      "name": "Quoted Values",
      "expression": "\\"[^\\"]*\\"",
      "color": "#43A047",
      "enabled": true
    },
    {
      "name": "Date Time",
      "expression": "\\\\[\\\\d{2}/\\\\d{2}/\\\\d{2}\\\\s\\\\d{2}:\\\\d{2}:\\\\d{2}\\\\.\\\\d{3}\\\\]",
      "color": "#9C27B0",
      "enabled": true
    },
    {
      "name": "GUID",
      "expression": "\\\\{[0-9A-Fa-f-]{36,}\\\\}",
      "color": "#CDDF2E",
      "enabled": true
    },
    {
      "name": "Error Keywords",
      "expression": "(?i)\\\\b(?:error|exception|fail|fatal|critical)\\\\b",
      "color": "#E53935",
      "bold": true,
      "enabled": true
    },
    {
      "name": "Warning Keywords",
      "expression": "(?i)\\\\b(?:warn|warning|caution)\\\\b",
      "color": "#FF6F00",
      "enabled": true
    },
    {
      "name": "Success Keywords",
      "expression": "(?i)\\\\b(?:success|ok|pass|complete)\\\\b",
      "color": "#14F71F",
      "enabled": true
    }
  ]
}"""
