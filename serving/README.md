# Public Serving Core

`content-rag-core.mjs` is the public-safe source of truth for the Content
Intelligence route's portable logic:

- deterministic private-artifact request classification;
- intent-specific lexical query expansion;
- weighted reciprocal-rank fusion for vector and lexical candidates;
- fenced OpenAI Responses API request construction;
- current model, latency, output, and embedding contracts;
- generated inline-citation validation.

The private portfolio Worker copies this module into its deployment bundle and
supplies the provider adapters: Cloudflare Workers AI embeddings, Vectorize
queries, OpenAI authentication, rate limiting, CORS, and response transport.
Secrets and unrelated private analytics routes remain outside this repository.

Run the portable contract tests with:

```bash
node --test serving/content-rag-core.test.mjs
```
