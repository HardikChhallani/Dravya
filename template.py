project_root/
├── README.md                     # Project documentation
├── .env                          # Environment variables
├── main.py                       # Streamlit app entry point
├── requirements.txt              # Project dependencies
└── src/
    ├── __init__.py
    ├── auth/
    │   ├── __init__.py
    │   └── authentication.py     # Authentication functionality
    ├── client/
    │   ├── __init__.py
    │   └── mcp_client.py         # MCP client implementation
    ├── services/
    │   ├── __init__.py
    │   └── groq_services.py      # Groq integration services
    ├── ui/
    │   ├── __init__.py
    │   ├── alternatives.py       # Alternatives tab UI and logic
    │   ├── generic_medicines.py  # Generic medicines tab UI and logic
    │   ├── medicine_finder.py    # Medicine finder tab UI and logic
    │   └── sidebar.py            # Sidebar UI components
    └── utils/
        ├── __init__.py
        └── config.py             # Configuration utilities