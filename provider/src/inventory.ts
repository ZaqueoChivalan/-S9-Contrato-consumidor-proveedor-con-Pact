export type InventoryItem = {
  sku: string;
  name: string;
  quantity: number;
  available: boolean;
};

const available: InventoryItem = {
  sku: "SKU-AVAILABLE",
  name: "Conference room A",
  quantity: 7,
  available: true
};

const outOfStock: InventoryItem = {
  sku: "SKU-OUT",
  name: "Conference room B",
  quantity: 0,
  available: false
};

let inventory: InventoryItem | null = available;

export const inventoryStates = {
  "inventory has stock for SKU": async () => { inventory = available; },
  "inventory has no stock for SKU": async () => { inventory = outOfStock; },
  "SKU does not exist in inventory": async () => { inventory = null; }
};

export function findInventory(sku: string): InventoryItem | null {
  if (!inventory || inventory.sku !== sku) return null;
  return inventory;
}
