# Compatibilidad consumidor proveedor con Pact

Proyecto académico en TypeScript que demuestra un contrato entre un servicio consumidor de reservaciones y una API proveedora de inventario. La frontera entre aplicaciones es HTTP: el consumidor consulta `GET /inventory/:sku` antes de aceptar una reservación.

## Arquitectura

```text
reservation-consumer  -- HTTP GET /inventory/:sku -->  inventory-provider
        |                                             |
   PactV3 + Vitest                              servidor HTTP real
        |                                             |
        +---- pacts/reservation-consumer-inventory-provider.json
```

El consumidor contiene `InventoryClient`, un cliente `fetch` real. Las pruebas PactV3 ejecutan ese cliente contra el servidor simulado de Pact y escriben el contrato en `pacts/`. La verificación usa `Verifier` contra una instancia real del proveedor, nunca contra el mock.

## Tres estados deterministas

| Estado del proveedor | SKU | Respuesta | Comportamiento consumidor |
| --- | --- | --- | --- |
| `inventory has stock for SKU` | `SKU-AVAILABLE` | `200` con cantidad positiva y `available: true` | acepta una solicitud de 2 unidades |
| `inventory has no stock for SKU` | `SKU-OUT` | `200` con `quantity: 0` y `available: false` | rechaza la reservación |
| `SKU does not exist in inventory` | `SKU-MISSING` | `404` con `error` y `sku` | devuelve inventario nulo |

Los estados modifican un almacén en memoria determinista antes de cada interacción verificada. Los cuerpos del contrato usan `MatchersV3` para SKU, nombre, cantidad y booleanos, conservando ejemplos legibles sin amarrar el contrato a un valor literal único.

## Versiones y comandos

- Node.js 20.x en CI
- TypeScript 5.7.2
- Pact `@pact-foundation/pact` 15.x
- Vitest 2.1.8

```bash
npm install
npm run typecheck
npm run test:consumer   # ejecuta el cliente real contra Pact y genera pacts/
npm run test:provider   # verifica las tres interacciones contra el proveedor real
npm test                # ambos pasos
```

El workflow `.github/workflows/contract-tests.yml` ejecuta typecheck, consumidor y proveedor en cada push y pull request. No se requiere Pact Broker.

## Evidencia y entrega

- Repositorio público: `https://github.com/ZaqueoChivalan/-S9-Contrato-consumidor-proveedor-con-Pact`
- Ejecución exitosa de GitHub Actions: `https://github.com/ZaqueoChivalan/-S9-Contrato-consumidor-proveedor-con-Pact/actions/runs/35482450795`
- Video de máximo 3 minutos: `https://REEMPLAZAR_ENLACE_DEL_VIDEO`

El enlace del video debe sustituirse después de grabar la demostración.

## Uso de inteligencia artificial

Se utilizó OpenAI Codex para proponer la estructura del proyecto, los escenarios PactV3, el cliente HTTP y el workflow. El resultado fue validado ejecutando el chequeo de tipos, las tres pruebas del consumidor y la verificación de las tres interacciones contra el servidor HTTP real del proveedor. No se incluyeron credenciales ni datos sensibles.
