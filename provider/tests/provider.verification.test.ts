import path from "node:path";
import { describe, beforeAll, afterAll, it } from "vitest";
import { Verifier } from "@pact-foundation/pact";
import { startProvider } from "../src/server.js";
import { inventoryStates } from "../src/inventory.js";

describe("Inventory provider verification", () => {
  let providerUrl: string;
  let close: (() => Promise<void>) | undefined;

  beforeAll(async () => {
    const running = await startProvider();
    providerUrl = running.url;
    close = () => new Promise((resolve, reject) => running.server.close((error) => error ? reject(error) : resolve()));
  });

  afterAll(async () => close?.());

  it("satisfies the consumer-generated Pact against the real provider", async () => {
    const verifier = new Verifier({
      provider: "inventory-provider",
      providerBaseUrl: providerUrl,
      pactUrls: [path.resolve("pacts/reservation-consumer-inventory-provider.json")],
      stateHandlers: inventoryStates,
      publishVerificationResult: false,
      providerVersion: "1.0.0",
      logLevel: "warn"
    });
    await verifier.verifyProvider();
  }, 30000);
});
