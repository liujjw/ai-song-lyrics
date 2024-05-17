# Setup
See local `.env.prod` folder (on Macbook) for environment variables to run local code as well as colab notebooks.

# Genius API
See the scripts for manual usage of the Genius API to scrape songs in Genius folder.

# Supabase
See `supabase` folder for scripts used to admin the Supabase database.

# Colab notebooks
`colab` folder contains notebooks for EDA, data cleaning and model training.

# OpenAI folder 
Frontend to dynamically generate lyrics. 

# Generate songs 
Async code to generate songs. Contains models, evaluation data, plots, and generated lyrics.
### Async + regex + Relational database backend + OpenAI GPT-4 backend + proper JSON message formatting
We used async to speed up our ingestion, each song is its own async task, and Python's async framework can support thousands of tasks concurrently. Running on Colab, we our disk IO and network bandwidth limits should be higher than the CPU and RAM limits of async. We used regex to parse song lyrics, relational database advanced queries like joins (relational database is actually fine for persistence since we have complex queries, although Pandas could speed up lyric part classification, the bottleneck is network IO). We use GPT-4 to extract keywords from lyrics to simulate what a user would type, and then the actual lyrics of the song as learning data. We used OpenAI's finetuning AI to generate a finetuned lyric LLM. We also need to make sure we format our chat messages for training properly for the API.