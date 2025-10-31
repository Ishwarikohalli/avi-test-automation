\# AVI Load Balancer Test Automation Framework



A Python-based modular test framework for VMware Avi Load Balancer API automation. This framework demonstrates configuration-driven automation, parallel task execution, and modular test structure.



\## Features



\- Configuration-Driven: All configurations stored in YAML files

\- Parallel Execution: Runs multiple test cases concurrently using ThreadPool

\- Modular Design: Separated API client, test runner, and validators

\- Authentication: Handles AVI API authentication with token management

\- Comprehensive Logging: Detailed execution logs with timestamps

\- Mock Components: SSH and RDP mock actions for testing

\- 4-Stage Workflow: Pre-Fetcher, Pre-Validation, Task/Trigger, Post-Validation



\## Project Structure

test\_automation/

├── main.py # Application entry point

├── config.yaml # Main configuration file

├── requirements.txt # Python dependencies

├── README.md # This documentation

├── test-framework/ # Core framework modules

│ ├── api\_client.py # AVI API client and HTTP operations

│ ├── test\_runner.py # Test execution engine with parallel processing

│ └── utils/ # Utility modules

│ ├── util.py # Configuration loading and logging setup

│ └── validators.py # Validation and mock functions

└── tests/ # Test case definitions

└── test\_disable\_virtual\_service.yaml





\## Prerequisites



\- Python 3.8 or higher

\- VMware AVI Load Balancer access (or mock API endpoint)



\##Development



\## Adding New Test Cases



Create a new YAML file in tests/ directory

Define the test workflow stages

Add the file path to config.yaml



\## Extending the Framework



Add new API methods in api\_client.py

Create new validators in validators.py

Implement additional mock actions

