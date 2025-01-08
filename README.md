# KastleTreeVersioningSystem
The system built here is a tree versioning and configuration management tool that allows users to manage hierarchical data structures (trees) with version control and tagging capabilities. Users interact with a single Tree class to create trees, add nodes and edges, tag specific configurations, and create new tree versions from existing tags. Internally, the system tracks versions using a TreeVersion class, enabling cloning, rollback, and branching. Each version can have its own set of nodes (TreeNode) and edges (TreeEdge). 

The design ensures efficient management of tree structures over time, supporting configuration snapshots, experimental branches, and safe rollbacks. A comprehensive test suite validates key operations, ensuring the system performs as expected in creating, modifying, and restoring tree configurations.

## Database Implementation

### Models
There are 5 models/classes used to build this system. 
#### **Tree**  
Represents the **root object** or logical container for versioned configurations. Each `Tree` can have multiple versions (snapshots) over time, allowing branching, tagging, and rollback of hierarchical data.


#### **TreeVersion**  
Acts as a **snapshot or version** of a `Tree` at a specific point in time. Each `TreeVersion` can clone data from previous versions and stores the state of nodes and edges at that point, enabling version control and branching.


#### **Tag**  
A label or identifier linked to a specific `TreeVersion`. Tags provide **human-readable names** (e.g., `v1.0`, `stable-release`) for easy access to specific versions, facilitating rollback, retrieval, and branching.


#### **TreeNode**  
Represents an **individual node** within a `TreeVersion`. Nodes store configuration data or hierarchical information, forming the building blocks of the tree’s structure.


#### **TreeEdge**  
Defines **relationships** or **connections** between `TreeNode` objects within a `TreeVersion`. Edges can contain metadata (e.g., weights, types) and help represent parent-child or dependency relationships between nodes.  

These models collectively enable a **versioned, hierarchical data structure** with full support for branching, tagging, and rollback operations.

---

### Migration Scipts 
The migration scripts for all the schema changes can be found in the [migrations folder](migrations/). It contains all the versions of the schema used for the implementation of the Tree Versioning System. 

### Efficient Indexing
The most two most queried attributes/keya are **tree_version_id** in the tables : TreeVersion, TreeNode and TreeEdge and **tag_name** in the Tag Table. 

To improve access times an index was made on these attributes to speed up access. See [schema.sql](db/schema.sql) 

1. Clone Repository
```
git clone https://github.com/Veshek/KastleTreeVersioningSystem.git
cd KastleTreeVersioningSystem
```

1. Create a Virtual Environment for Clean Package Management
To set up a virtual environment for this project, run the following command inside the project directory:

```
python -m venv venv
```

2. Activating the Virtual Environment
```
On macOS/Linux:
source venv/bin/activate

On Windows:
venv\Scripts\activate
```

3. Install Dependencies
```
After activating the virtual environment, install the required dependencies:

pip install -r requirements.txt
```

## Running Tests
The test framework used is pytest
```
# To Run Unit Tests
pytest .\tests\unit_tests.py -vv

# To Run Integration Tests
pytest .\tests\integration_tests.py -vv
```
## Running main.py

```
python src.main
```



