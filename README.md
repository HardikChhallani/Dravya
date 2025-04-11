# Medicine Finder

A Streamlit-based application powered by Ekacare MCP (Medical Content Provider) tools for finding medicine information, alternatives, and generic options in the Indian healthcare context.

[![GitHub](https://img.shields.io/badge/GitHub-HardikChhallani-blue?style=flat&logo=github)](https://github.com/HardikChhallani)


## Features

- User authentication with login/logout functionality
- Three main sections powered by Ekacare MCP tools:
  1. Medicine Alternatives Finder: Find therapeutic alternatives with similar active ingredients
  2. Generic Medicine Search: Discover cost-effective generic alternatives to branded medicines
  3. Detailed Medicine Information: Access comprehensive drug information from Indian healthcare databases
- Secure API key management using environment variables
- Integration with Groq LLM and Ekacare MCP services for accurate Indian medicine data

## Project Structure

```
├── src/
│   ├── auth/
│   │   ├── auth_manager.py    # Authentication management
│   │   └── config.yaml        # User credentials configuration
│   ├── client/
│   │   └── mcp_client.py      # Ekacare MCP client implementation
│   ├── services/
│   │   ├── groq_service.py    # Groq LLM service integration
│   │   └── mcp_service.py     # MCP service orchestration
│   ├── ui/
│       ├── alternatives.py    # Medicine alternatives UI
│       ├── generic_medicines.py # Generic medicines UI
│       └── medicine_finder.py  # Medicine information UI
|── main.py
├── .env                       # Environment variables
└── requirements.txt           # Project dependencies
```

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure environment variables in `.env`:
   ```
   GROQ_API_KEY=your_groq_api_key
   EKA_CLIENT_ID=your_eka_client_id        # Required for Ekacare MCP API access
   EKA_CLIENT_SECRET=your_eka_client_secret # Required for Ekacare MCP API access
   ```

   Note: Obtain your Ekacare API credentials by registering at https://api.eka.care

3. Run the application:
   ```bash
   streamlit run src/app.py
   ```

## Default Login Credentials

- Username: admin
- Password: admin123

## Features by Tab

1. **Alternatives Tab**
   - Find alternative medicines using Ekacare's comprehensive Indian medicine database
   - Compare prices and compositions of Indian branded medications
   - Get therapeutic equivalents available in the Indian market

2. **Generic Medicines Tab**
   - Search for Indian generic alternatives to branded medicines
   - Access Ekacare's database of approved generic medications
   - View detailed price comparisons and bioequivalence information
   - Get manufacturer information for generic medicines

3. **Find Your Medicines Tab**
   - Get detailed information about medicines from Ekacare's Indian drug database
   - Access official drug information, including:
     - Approved uses and dosages
     - Side effects and precautions
     - Drug interactions
     - Storage requirements
     - Manufacturing details

## Ekacare MCP Integration

This application leverages Ekacare's Medical Content Provider (MCP) tools to provide accurate and reliable information about medicines available in India. The integration includes:

- **Indian Branded Drug Search**: Search and retrieve information about Indian branded medications
- **Treatment Protocol Search**: Access Indian treatment guidelines and protocols
- **Protocol Publishers**: Get information from authorized Indian medical publishers

All drug information is sourced from Ekacare's verified database of Indian medications, ensuring accuracy and relevance for the Indian healthcare context.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Hardik Chhallani**
- GitHub: [@HardikChhallani](https://github.com/HardikChhallani)

---

Built with ❤️ using Streamlit, Groq LLM, and Ekacare MCP
