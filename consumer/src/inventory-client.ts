export type InventoryItem = {
  sku: string;
  name: string;
  quantity: number;
  available: boolean;
};

export class InventoryNotFoundError extends Error {}

export class InventoryClient {
  constructor(private readonly baseUrl: string) {}

  async getInventory(sku: string): Promise<InventoryItem | null> {
    const response = await fetch(`${this.baseUrl}/inventory/${encodeURIComponent(sku)}`);

    if (response.status === 404) return null;
    if (!response.ok) throw new Error(`Inventory provider returned ${response.status}`);

    const body = (await response.json()) as InventoryItem;
    return body;
  }

  async canAcceptReservation(sku: string, requestedQuantity: number): Promise<boolean> {
    const item = await this.getInventory(sku);
    return item !== null && item.available && item.quantity >= requestedQuantity;
  }
}
