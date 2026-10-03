### Rag Knowledge Assistant 
A local AI assistant built with React, Flask, Chroma, and Ollama. It answers questions about onboarding, product support, security, and workplace policies using provided documents and supporting sources.
Setup and Run
Start Ollama and download the models:
ollama serve

In another terminal:
ollama pull llama3.2
ollama pull nomic-embed-text

Set up and start the backend:
cd server
pipenv install
cp .env.example .env
pipenv run python seed_knowledge_base.py
pipenv run flask --app app run --debug --port 5555

Start the frontend in another terminal:
cd client
npm install
npm run dev

Open http://localhost:5173.
Configuration
The .env file configures the Ollama URL, generation and embedding models, Chroma storage path, collection name, knowledge base path, retrieval count, temperature, and frontend origin. Use the defaults in .env.example.
API and Workflow
- GET /api/health checks the backend.
- POST /api/ask accepts a question and returns an answer with sources.
React sends the question to Flask. The backend retrieves relevant document chunks from Chroma, builds a prompt, and asks Ollama to generate an answer. React displays the answer and sources.
Verification
Seeding successfully loaded 4 documents and stored 9 chunks.
Sample Question	Answer and Sources
What should I do if I cannot log into the dashboard?	Pending verification
Why are source-backed answers important?	Pending verification
What should employees do with suspicious emails?	Pending verification


Limitations
The knowledge base is small, local generation can be slow, and answers require source review. Future improvements include better error handling, retrieval, and source previews.