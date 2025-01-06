# KastleTreeVersioningSystem
Sub System Design & Implementation Interview @ Kastle.Ai

## Clone Repo
git clone https://github.com/Veshek/KastleTreeVersioningSystem.git
cd KastleTreeVersioningSystem

## Setup
1. Creating a Virtual Environment
To set up a virtual environment for this project, run the following command in the project directory:

python -m venv venv

2. Activating the Virtual Environment
On macOS/Linux:
source venv/bin/activate

On Windows:
venv\Scripts\activate

3. Installing Dependencies
After activating the virtual environment, install the required dependencies:

pip install -r requirements.txt

4. Deactivating the Virtual Environment
Once you're done, deactivate the virtual environment:

deactivate

## Database Setup
Initialize the database by running:

python -c "from db.database import init_db; init_db()"

This creates the necessary tables (Tree, TreeNode, TreeEdge, and Tag) in an SQLite database.

## Running Tests

To verify the implementation and ensure all features work correctly, run the following command:


## pytest tests/
Usage
Use the scripts in src/main.py to manage trees, nodes, edges, and version tags.
This system allows for:
Creating new tree configurations
Adding nodes and edges to trees
Tagging configurations for versioning
Traversing and restoring previous configurations

## Project Structure


tree_versioning_system/
│
├── db/
│   ├── schema.sql  # SQL schema for tables
│   ├── database.py # SQLite connection and queries
│
├── src/
│   ├── main.py     # Core logic 
│
├── tests/
│   ├── test.py  # Unit tests
│
├── venv/  # Virtual environment (ignored in .gitignore)
│
├── requirements.txt
├── config.py
└── README.md
