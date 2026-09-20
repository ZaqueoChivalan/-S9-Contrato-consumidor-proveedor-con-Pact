import { describe, expect, it } from "vitest";
import { PactV3, MatchersV3 } from "@pact-foundation/pact";
import { InventoryClient } from "../src/inventory-client.js";

const { string, integer, boolean } = MatchersV3;

describe("Inventory consumer contract", () => {
  it("accepts a reservation when the product is available", async () => {
    const provider = new PactV3({ consumer: "reservation-consumer", provider: "inventory-provider", dir: "pacts" });
    provider.addInteraction({
      states: [{ description: "inventory has stock for SKU" }],
      uponReceiving: "a request for available inventory",
      withRequest: { method: "GET", path: "/inventory/SKU-AVAILABLE" },
      willRespondWith: {
        status: 200,
        headers: { "content-type": "application/json" },
        body: { sku: string("SKU-AVAILABLE"), name: string("Conference room A"), quantity: integer(7), available: boolean(true) }
      }
    });

    await provider.executeTest(async (mockServer) => {
      const client = new InventoryClient(mockServer.url);
      await expect(client.canAcceptReservation("SKU-AVAILABLE", 2)).resolves.toBe(true);
    });
  });

  it("rejects a reservation when the product has no stock", async () => {
    const provider = new PactV3({ consumer: "reservation-consumer", provider: "inventory-provider", dir: "pacts" });
    provider.addInteraction({
      states: [{ description: "inventory has no stock for SKU" }],
      uponReceiving: "a request for out of stock inventory",
      withRequest: { method: "GET", path: "/inventory/SKU-OUT" },
      willRespondWith: {
        status: 200,
        headers: { "content-type": "application/json" },
        body: { sku: string("SKU-OUT"), name: string("Conference room B"), quantity: integer(0), available: boolean(false) }
      }
    });

    await provider.executeTest(async (mockServer) => {
      const client = new InventoryClient(mockServer.url);
      await expect(client.canAcceptReservation("SKU-OUT", 1)).resolves.toBe(false);
    });
  });

  it("does not accept a reservation for an unknown SKU", async () => {
    const provider = new PactV3({ consumer: "reservation-consumer", provider: "inventory-provider", dir: "pacts" });
    provider.addInteraction({
      states: [{ description: "SKU does not exist in inventory" }],
      uponReceiving: "a request for an unknown SKU",
      withRequest: { method: "GET", path: "/inventory/SKU-MISSING" },
      willRespondWith: { status: 404, headers: { "content-type": "application/json" }, body: { error: string("SKU not found"), sku: string("SKU-MISSING") } }
    });

    await provider.executeTest(async (mockServer) => {
      const client = new InventoryClient(mockServer.url);
      await expect(client.getInventory("SKU-MISSING")).resolves.toBeNull();
    });
  });
});
