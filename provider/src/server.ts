import { createServer, type Server } from "node:http";
import { findInventory } from "./inventory.js";

export function startProvider(port = 0): Promise<{ server: Server; url: string }> {
  const server = createServer((request, response) => {
    const match = request.url?.match(/^\/inventory\/([^/]+)$/);
    if (request.method !== "GET" || !match) {
      response.writeHead(404, { "content-type": "application/json" });
      response.end(JSON.stringify({ error: "route not found" }));
      return;
    }

    const sku = decodeURIComponent(match[1]);
    const item = findInventory(sku);
    response.setHeader("content-type", "application/json");
    if (!item) {
      response.writeHead(404);
      response.end(JSON.stringify({ error: "SKU not found", sku }));
      return;
    }

    response.writeHead(200);
    response.end(JSON.stringify(item));
  });

  return new Promise((resolve) => {
    server.listen(port, "127.0.0.1", () => {
      const address = server.address();
      const actualPort = typeof address === "object" && address ? address.port : port;
      resolve({ server, url: `http://127.0.0.1:${actualPort}` });
    });
  });
}

if (process.argv[1]?.endsWith("server.ts")) {
  startProvider(3001).then(({ url }) => console.log(`Inventory provider listening at ${url}`));
}
