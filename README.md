# deepmind-code

deepmind-code is a command-line interface (CLI) tool designed to assist developers with their coding tasks directly from the terminal. By integrating various large language models (LLMs), this tool allows you to interact with your codebase, automate file modifications, and analyze system errors without having to leave your terminal environment.

## Key Features

- **Codebase Interaction**: Engage in a dialogue with an AI that understands your project's directory structure and context.
- **Automated File Editing**: Modify source code based on natural language instructions, featuring a preview of changes before they are applied.
- **Error Identification and Fixes**: Analyze terminal error logs and receive instant solutions or suggestions for improvement.
- **Code Review**: Gain insights on architecture, potential bugs, and best practices from a senior developer's perspective.
- **Multi-Provider Support**: Seamlessly integrated with popular AI providers including OpenAI, Google Gemini, Anthropic, Groq, and Ollama for local execution.

## System Requirements

- Python version 3.9 or newer.
- Internet access (for cloud providers) or an Ollama installation (for local usage).

## Installation

Follow the steps below to install deepmind-code on your system:

1. Download or clone this repository to your computer.
2. Navigate to the project directory:
   ```bash
   cd deepmind-code
   ```
3. Install the package in editable mode to ensure changes are synchronized:
   ```bash
   pip install -e .
   ```

Once the installation is complete, you can invoke the application using the `dmc` command in your terminal.

## Configuration

Before you begin, you need to set up the default model and the API keys for the providers you intend to use.

### Setting Up AI Providers

You can configure the API keys for each provider using the following commands:

- **Google Gemini**:
  ```bash
  dmc config --gemini-key "YOUR_API_KEY" --model gemini/gemini-pro
  ```
- **OpenAI**:
  ```bash
  dmc config --openai-key "YOUR_API_KEY" --model gpt-4o
  ```
- **Groq**:
  ```bash
  dmc config --groq-key "YOUR_API_KEY" --model groq/llama-3.3-70b-versatile
  ```
- **Ollama (Local)**:
  ```bash
  dmc config --model ollama/llama3
  ```

To view your current configuration, simply run the following command:
```bash
dmc config
```

## Usage Guide

### 1. Discuss with AI (Chat)
Use this feature to ask questions about application logic or your project's overall structure.
```bash
dmc chat "Explain the data flow in the src folder"
```

### 2. Modify Code (Edit)
This feature allows the AI to write code directly into your project files. The application will display a preview of the changes and ask for your approval before saving the results.
```bash
dmc edit filename.py "add input validation to the login function"
```
Note: You do not need to provide the full file path. deepmind-code will automatically search for the file within your project.

### 3. Fix Errors (Fix)
If you encounter an error message or traceback in your terminal, you can send it directly to the AI for analysis.
```bash
python app.py 2>&1 | dmc fix
```
Alternatively, you can manually paste the error message when prompted by the application after running `dmc fix`.

### 4. Project Review
Analyze the code quality or overall project structure within a specific folder.
```bash
dmc review src/
```

### 5. Automated Agent Mode (Agent)
This powerful feature allows the AI to perform complex, multi-step tasks. The AI can read files, edit files, and execute terminal commands autonomously with your permission.
```bash
dmc agent "add user registration feature complete with unit tests"
```

## License
This project is distributed under the MIT license. Please refer to the LICENSE file for more details.
