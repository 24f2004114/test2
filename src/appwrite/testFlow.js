async function query(data) {
  const response = await fetch(
    "https://router.huggingface.co/together/v1/completions",
    {
      headers: {
        Authorization: "Bearer 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",
        "Content-Type": "application/json",
      },
      method: "POST",
      body: JSON.stringify(data),
    }
  );
  const result = await response.json();
  return result;
}

query({
  model: "moonshotai/Kimi-K2-Instruct",   // ✅ required
  prompt: "Generate five easy-level questions on rotational motion", // ✅ use 'prompt' instead of 'inputs'
  max_tokens: 200                         // ✅ recommended to avoid very short answers
}).then((response) => {
  console.log(JSON.stringify(response, null, 2));
});
