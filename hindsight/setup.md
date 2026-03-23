# Hindsight Setup

1. Create an account at `https://hindsight.vectorize.io` and log in.
2. Create a new pipeline for your project.
3. Copy the pipeline ID from the pipeline settings page.
4. Generate an API key from your account settings.
5. Add the following values to the root `.env` file:
   - `HINDSIGHT_API_KEY`
   - `HINDSIGHT_PIPELINE_ID`

The backend uses these values to fetch and save the student memory document during chats, quizzes, and study-plan generation.
