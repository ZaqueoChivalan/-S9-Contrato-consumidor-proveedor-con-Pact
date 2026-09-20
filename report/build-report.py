from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Preformatted, KeepTogether
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "pdf" / "entrega-pact-consumidor-proveedor.pdf"
OUT.parent.mkdir(parents=True, exist_ok=True)

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="CoverTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=24, leading=29, textColor=colors.HexColor("#12304A"), alignment=TA_CENTER, spaceAfter=12))
styles.add(ParagraphStyle(name="CoverSub", parent=styles["Normal"], fontSize=12, leading=17, textColor=colors.HexColor("#426174"), alignment=TA_CENTER, spaceAfter=22))
styles.add(ParagraphStyle(name="Section", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=16, leading=20, textColor=colors.HexColor("#087E8B"), spaceBefore=10, spaceAfter=8))
styles.add(ParagraphStyle(name="Body2", parent=styles["BodyText"], fontSize=10, leading=14, spaceAfter=8, textColor=colors.HexColor("#243746")))
styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=8.5, leading=11, textColor=colors.HexColor("#3B4D5A")))
styles.add(ParagraphStyle(name="TableHead", parent=styles["Small"], textColor=colors.white))
styles.add(ParagraphStyle(name="Caption", parent=styles["BodyText"], fontSize=8.5, leading=11, textColor=colors.HexColor("#5B6F7C"), alignment=TA_CENTER, spaceBefore=4, spaceAfter=12))

def P(text, style="Body2"):
    return Paragraph(text, styles[style])

def footer(canvas, doc):
    return

story = []
story += [Spacer(1, 22*mm), P("Compatibilidad entre consumidor y proveedor", "CoverTitle"), P("Servicio de reservaciones e inventario con PactV3 y Vitest", "CoverSub")]
story += [P("Entrega académica", "Small"), Spacer(1, 8*mm)]
diagram = Table([[P("CONSUMER\nreservation-consumer", "Small"), P("CONTRATO\nPactV3 / pacts/*.json", "Small"), P("PROVIDER\ninventory-provider", "Small")]], colWidths=[52*mm, 62*mm, 52*mm], rowHeights=[22*mm])
diagram.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#E8F4F5")), ("BOX", (0,0), (-1,-1), 1, colors.HexColor("#087E8B")), ("INNERGRID", (0,0), (-1,-1), .5, colors.HexColor("#A9CDD1")), ("ALIGN", (0,0), (-1,-1), "CENTER"), ("VALIGN", (0,0), (-1,-1), "MIDDLE")]))
story += [diagram, P("El consumidor consulta GET /inventory/:sku antes de aceptar una reservación. El contrato se genera contra un mock de Pact y luego se verifica contra el servidor HTTP real del proveedor.", "Caption"), Spacer(1, 16*mm), P("Resultado de validación", "Section"), P("Consumidor: 3 interacciones aprobadas. Proveedor: 3 interacciones aprobadas contra la implementación real, incluyendo los estados de disponibilidad, sin existencias y SKU inexistente.", "Body2"), PageBreak()]

story += [P("1. Frontera y arquitectura", "Section"), P("La frontera elegida es una API HTTP entre dos aplicaciones independientes. El consumidor no conoce el almacén del proveedor: solo interpreta el código HTTP y el JSON de GET /inventory/:sku. El proveedor expone un servidor Node HTTP real con un almacén determinista en memoria.", "Body2")]
arch = Table([[P("Consumidor", "TableHead"), P("Contrato", "TableHead"), P("Proveedor", "TableHead")], [P("InventoryClient\nfetch real\ncanAcceptReservation", "Small"), P("PactV3\nMatchersV3\n3 interacciones", "Small"), P("GET /inventory/:sku\nstateHandlers\nVerifier", "Small")]], colWidths=[58*mm, 58*mm, 58*mm])
arch.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#12304A")), ("TEXTCOLOR", (0,0), (-1,0), colors.white), ("BACKGROUND", (0,1), (-1,-1), colors.HexColor("#F1F7F8")), ("GRID", (0,0), (-1,-1), .5, colors.HexColor("#B8CDD4")), ("VALIGN", (0,0), (-1,-1), "TOP"), ("LEFTPADDING", (0,0), (-1,-1), 8), ("RIGHTPADDING", (0,0), (-1,-1), 8), ("TOPPADDING", (0,0), (-1,-1), 8), ("BOTTOMPADDING", (0,0), (-1,-1), 8)]))
story += [arch, P("Estados del dominio", "Section")]
state_data = [[P("Estado", "TableHead"), P("SKU", "TableHead"), P("Respuesta", "TableHead"), P("Resultado", "TableHead")], [P("inventory has stock for SKU", "Small"), P("SKU-AVAILABLE", "Small"), P("200, quantity 7", "Small"), P("Acepta", "Small")], [P("inventory has no stock for SKU", "Small"), P("SKU-OUT", "Small"), P("200, quantity 0", "Small"), P("Rechaza", "Small")], [P("SKU does not exist in inventory", "Small"), P("SKU-MISSING", "Small"), P("404, error + sku", "Small"), P("Nulo", "Small")]]
st = Table(state_data, colWidths=[62*mm, 32*mm, 36*mm, 28*mm], repeatRows=1)
st.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#087E8B")), ("TEXTCOLOR", (0,0), (-1,0), colors.white), ("GRID", (0,0), (-1,-1), .4, colors.HexColor("#B8CDD4")), ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F1F7F8")]), ("VALIGN", (0,0), (-1,-1), "MIDDLE"), ("LEFTPADDING", (0,0), (-1,-1), 5), ("RIGHTPADDING", (0,0), (-1,-1), 5), ("TOPPADDING", (0,0), (-1,-1), 6), ("BOTTOMPADDING", (0,0), (-1,-1), 6)]))
story += [st, PageBreak()]

story += [P("2. Generación del contrato", "Section"), P("El cliente HTTP real se ejecuta contra el servidor simulado de Pact. MatchersV3 permite validar el tipo y la forma de los datos variables: string para identificadores y nombres, integer para cantidades y boolean para disponibilidad.", "Body2")]
contract_extract = '''provider.addInteraction({\n  states: [{ description: "inventory has stock for SKU" }],\n  uponReceiving: "a request for available inventory",\n  withRequest: { method: "GET", path: "/inventory/SKU-AVAILABLE" },\n  willRespondWith: {\n    status: 200,\n    body: { sku: string("SKU-AVAILABLE"),\n      name: string("Conference room A"),\n      quantity: integer(7), available: boolean(true) }\n  }\n});\n\nawait provider.executeTest(async (mockServer) => {\n  const client = new InventoryClient(mockServer.url);\n  await expect(client.canAcceptReservation("SKU-AVAILABLE", 2))\n    .resolves.toBe(true);\n});'''
story += [Preformatted(contract_extract, styles["Code"]), P("Extracto de consumer/tests/inventory.pact.test.ts", "Caption"), P("Resultado observado: `inventory.pact.test.ts (3 tests)`, los tres requests coinciden con el mock y se genera `pacts/reservation-consumer-inventory-provider.json`.", "Body2")]
pact_extract = '''"consumer": { "name": "reservation-consumer" },\n"provider": { "name": "inventory-provider" },\n"interactions": [\n  { "description": "a request for an unknown SKU",\n    "providerStates": [{ "name": "SKU does not exist in inventory" }],\n    "request": { "method": "GET", "path": "/inventory/SKU-MISSING" },\n    "response": { "status": 404 } },\n  ... 2 interacciones adicionales\n]'''
story += [Preformatted(pact_extract, styles["Code"]), P("Extracto legible del Pact generado", "Caption"), PageBreak()]

story += [P("3. Verificación del proveedor real", "Section"), P("La prueba arranca el servidor del proveedor en un puerto local, registra stateHandlers para cada estado del dominio y ejecuta Verifier con el Pact generado. Por tanto, las respuestas pasan por la implementación real de GET /inventory/:sku.", "Body2")]
verification = '''Verifying a pact between reservation-consumer and inventory-provider\n\nGiven SKU does not exist in inventory\n  status code 404 (OK)\n  matching body (OK)\n\nGiven inventory has stock for SKU\n  status code 200 (OK)\n  matching body (OK)\n\nGiven inventory has no stock for SKU\n  status code 200 (OK)\n  matching body (OK)\n\nprovider.verification.test.ts (1 test)\n1 passed'''
story += [Preformatted(verification, styles["Code"]), P("Extracto de la ejecución de npm run test:provider", "Caption"), P("La verificación confirma códigos HTTP, encabezados y cuerpos en los tres escenarios. El workflow de GitHub Actions repite typecheck, pruebas del consumidor y verificación del proveedor en cada push y pull request.", "Body2"), P("Enlaces de entrega", "Section")]
links = [[P("Repositorio público", "Small"), P("https://github.com/ZaqueoChivalan/-S9-Contrato-consumidor-proveedor-con-Pact", "Small")], [P("GitHub Actions", "Small"), P("https://github.com/ZaqueoChivalan/-S9-Contrato-consumidor-proveedor-con-Pact/actions/runs/35482450795", "Small")], [P("Video <= 3 minutos", "Small"), P("https://drive.google.com/file/d/15PqFFNDDEeJYe82dScSbv6Sf5-XcHKnD/view?usp=sharing", "Small")]]
lt = Table(links, colWidths=[42*mm, 116*mm])
lt.setStyle(TableStyle([("GRID", (0,0), (-1,-1), .4, colors.HexColor("#B8CDD4")), ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#E8F4F5")), ("VALIGN", (0,0), (-1,-1), "TOP"), ("LEFTPADDING", (0,0), (-1,-1), 6), ("RIGHTPADDING", (0,0), (-1,-1), 6), ("TOPPADDING", (0,0), (-1,-1), 7), ("BOTTOMPADDING", (0,0), (-1,-1), 7)]))
story += [lt, Spacer(1, 8*mm), P("La entrega incluye el repositorio público, la ejecución exitosa de CI y el video demostrativo.", "Small")]

doc = SimpleDocTemplate(str(OUT), pagesize=A4, rightMargin=18*mm, leftMargin=18*mm, topMargin=16*mm, bottomMargin=18*mm, title="Compatibilidad entre consumidor y proveedor")
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(OUT)
