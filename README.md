Chilling with cool upsonic agents!

# Usage

First, Clone the repo

## Using Docker

1.  Ensure Docker is installed on your machine. For more information, visit the official [Docker documentation](https://docs.docker.com/).

2.  **Build the Docker image:**
    ```sh
    docker-compose build upsonic_agent
    ```

3.  **Run the Docker container:**
    ```sh
    docker-compose up -d --no-build upsonic_agent
    ```
    **Note:** This will work only if you have the required credentials in the `.env` file.
    **Note:** You can inspect the running container by running `docker-compose logs -f upsonic_agent`!!!!!!!!!!!


5.  **Stop the Docker container:**
    ```sh
    docker-compose down 
    ```

## Running Locally in the Shell

1.  Install `uv` by following the instructions [here](https://github.com/astral-sh/uv#installation).


2.  **Install the dependencies and package:**
    ```sh
    uv sync --all-groups
    ```
3. **Activate venv:**
   ```sh
    .venv\Scripts\activate
    ```
4. **Run the script:**
   ```sh
    uv run python -m src.app.agent
    ```

```markdown

UPSONIC_AGENT/
├── src/
│ └── app/
│ ├── __init__.py
│ ├── agent.py
│ ├── constants.py
│ ├── result.md   #You can see the pre-generated result here!!!!
│ └── tools.py
├── .dockerignore
├── .env.example
├── .gitignore
├── .python-version
├── docker-compose.yml
├── Dockerfile
├── main.py
├── pyproject.toml
├── README.md
└── uv.lock
```
