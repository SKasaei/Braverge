



from google import genai

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client(api_key = "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")

response = client.models.generate_content(
    model="gemini-2.5-flash", contents="Explain how AI works in a few words"
)
print(response.text)