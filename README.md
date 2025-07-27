# Nutrition MCP Server Setup

## Prerequisites
- Python 3.8+ (pre-installed on most systems)
- USDA API key (free): https://fdc.nal.usda.gov/api-guide.html

## Installation

1. **Download files** to a folder called `nutrition-mcp-server`

2. **Create virtual environment and install:**
```bash
cd nutrition-mcp-server
python3 -m venv nutrition-env
source nutrition-env/bin/activate
pip install mcp requests
```

3. **Test the server:**
```bash
USDA_API_KEY=your_key_here python main.py
```
Press Ctrl+C to stop.

## Claude Desktop Configuration

4. **Generate config automatically:**
```bash
python generate_config.py
```

This will output the exact configuration and file location for your system.

5. **Add your API key** to the generated config, replacing `YOUR_API_KEY_HERE`

6. **Restart Claude Desktop**

## Usage
- "Search for tofu products"
- "Get nutrition for FDC ID 16213"
- "What are the macros for chicken breast?"

## Troubleshooting
- **Virtual environment:** If `source` command fails, try `nutrition-env\Scripts\activate` on Windows
- **API errors:** Verify your USDA API key is correct
- **Path errors:** Use absolute paths from `generate_config.py` output
- **Python not found:** Try `python` instead of `python3` on Windows

---

## Meal Planning Project Setup

Want to create AI-powered meal plans? Here's how to set up a nutrition-focused Claude project:

### 1. Create New Project
- Open Claude Desktop
- Click "+" to create new project
- Name it "Meal Planner"

### 2. Add System Prompt
- Click the settings icon in your project
- Copy the system prompt from [meal_planner_prompt.md](meal_planner_prompt.md)
- Edit the **USER INPUTS** section:
  - Change diet type (vegan, keto, etc.)
  - Update calorie/protein targets
  - Replace fixed meals with your breakfast/snacks and their macros

### 3. Usage
Start conversations with: "I want to plan lunch and dinner for this week. Let's brainstorm some ideas."

The AI will use the nutrition MCP server to calculate exact portions and create detailed meal plans with shopping lists.