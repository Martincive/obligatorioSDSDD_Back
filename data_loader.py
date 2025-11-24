import pandas as pd
from langchain_core.documents import Document
from settings import DATA_FILE

def load_excel_as_documents():
    productos = pd.read_excel(DATA_FILE, sheet_name="Productos")
    clientes = pd.read_excel(DATA_FILE, sheet_name="Clientes")
    ventas = pd.read_excel(DATA_FILE, sheet_name="Ventas")

    ventas_full = ventas.merge(productos, on="IdProducto").merge(clientes, on="IdCliente")

    # Convertir fechas a datetime
    ventas_full["FechaVenta"] = pd.to_datetime(ventas_full["FechaVenta"])
    ventas_full["Año"] = ventas_full["FechaVenta"].dt.year
    ventas_full["Mes"] = ventas_full["FechaVenta"].dt.month_name()
    ventas_full["MesNum"] = ventas_full["FechaVenta"].dt.month

    docs = []


    for _, row in ventas_full.iterrows():
        text = (
            f"Venta {row['IdVenta']} realizada el {row['FechaVenta'].date()}. "
            f"Cliente: {row['NombreCliente']} (Ciudad: {row['Ciudad']}). "
            f"Producto: {row['NombreProducto']} (Categoría: {row['Categoria']}). "
            f"Cantidad vendida: {row['Cantidad']}. "
            f"Precio unitario: {row['Precio']}. "
            f"Total venta: {row['Cantidad'] * row['Precio']}."
        )

        metadata = {
            "tipo": "venta",
            "id_venta": int(row["IdVenta"]),
            "cliente": row["NombreCliente"],
            "producto": row["NombreProducto"],
            "categoria": row["Categoria"],
            "ciudad": row["Ciudad"],
            "año": int(row["Año"]),
            "mes": row["Mes"],
        }

        docs.append(Document(page_content=text, metadata=metadata))


    agg_prod = ventas_full.groupby(
        ["IdProducto", "NombreProducto", "Categoria"]
    ).agg(
        total_unidades=("Cantidad", "sum"),
        total_ventas=("Cantidad", lambda x: (x * ventas_full.loc[x.index, "Precio"]).sum()),
        clientes=("NombreCliente", lambda x: ", ".join(sorted(set(x))))
    ).reset_index()

    for _, row in agg_prod.iterrows():
        text = (
            f"Producto agregado: {row['NombreProducto']} de la categoría {row['Categoria']}. "
            f"Unidades totales vendidas: {row['total_unidades']}. "
            f"Ventas totales: {row['total_ventas']}. "
            f"Clientes que lo compraron: {row['clientes']}."
        )
        docs.append(Document(
            page_content=text,
            metadata={
                "tipo": "producto_agg",
                "producto": row["NombreProducto"],
                "categoria": row["Categoria"]
            }
        ))


    agg_clientes = ventas_full.groupby(
        ["IdCliente", "NombreCliente", "Ciudad"]
    ).agg(
        unidades=("Cantidad", "sum"),
        productos=("NombreProducto", lambda x: ", ".join(sorted(set(x)))),
        categorias=("Categoria", lambda x: ", ".join(sorted(set(x)))),
    ).reset_index()

    for _, row in agg_clientes.iterrows():
        text = (
            f"Cliente agregado: {row['NombreCliente']} de {row['Ciudad']}. "
            f"Total de unidades compradas: {row['unidades']}. "
            f"Productos comprados: {row['productos']}. "
            f"Categorías consumidas: {row['categorias']}."
        )

        docs.append(Document(
            page_content=text,
            metadata={
                "tipo": "cliente_agg",
                "cliente": row["NombreCliente"],
                "ciudad": row["Ciudad"],
            }
        ))


    agg_cat = ventas_full.groupby("Categoria").agg(
        unidades=("Cantidad", "sum"),
        ingresos=("Cantidad", lambda x: (x * ventas_full.loc[x.index, "Precio"]).sum()),
    ).reset_index()

    for _, row in agg_cat.iterrows():
        text = (
            f"Categoría agregada: {row['Categoria']}. "
            f"Unidades totales vendidas: {row['unidades']}. "
            f"Ingresos totales: {row['ingresos']}."
        )

        docs.append(Document(
            page_content=text,
            metadata={"tipo": "categoria_agg", "categoria": row["Categoria"]}
        ))


    agg_mes = ventas_full.groupby(["Año", "Mes", "MesNum"]).agg(
        unidades=("Cantidad", "sum"),
        ingresos=("Cantidad", lambda x: (x * ventas_full.loc[x.index, "Precio"]).sum()),
    ).reset_index()

    for _, row in agg_mes.iterrows():
        text = (
            f"Resumen mensual: {row['Mes']} de {row['Año']}. "
            f"Unidades vendidas: {row['unidades']}. "
            f"Ingresos generados: {row['ingresos']}."
        )

        docs.append(Document(
            page_content=text,
            metadata={
                "tipo": "mes_agg",
                "mes": row["Mes"],
                "año": int(row["Año"]),
            }
        ))


    productos_lista = ", ".join(sorted(productos["NombreProducto"]))

    docs.append(Document(
        page_content=f"Lista completa de productos disponibles: {productos_lista}.",
        metadata={"tipo": "global"}
    ))

    ventas_por_producto = ventas_full.groupby(
        ["NombreProducto", "Categoria"]
    ).agg(
        total_unidades=("Cantidad", "sum"),
        total_ingresos=("Cantidad", lambda x: (x * ventas_full.loc[x.index, "Precio"]).sum())
    ).reset_index()

    lines = []
    for _, row in ventas_por_producto.iterrows():
        lines.append(
            f"{row['NombreProducto']} (categoría {row['Categoria']}): "
            f"{row['total_unidades']} unidades, "
            f"${row['total_ingresos']} ingresos."
        )

    producto_totales_text = (
            "Ventas totales por producto (resumen global):\n" +
            "\n".join(lines)
    )

    docs.append(Document(
        page_content=producto_totales_text,
        metadata={"tipo": "producto_totales_global"}
    ))
    ventas_por_cliente = ventas_full.groupby(
        ["NombreCliente", "Ciudad"]
    ).agg(
        total_unidades=("Cantidad", "sum"),
        total_ingresos=("Cantidad", lambda x: (x * ventas_full.loc[x.index, "Precio"]).sum()),
        productos=("NombreProducto", lambda x: ", ".join(sorted(set(x)))),
        categorias=("Categoria", lambda x: ", ".join(sorted(set(x))))
    ).reset_index()

    lines_cliente = []
    for _, row in ventas_por_cliente.iterrows():
        lines_cliente.append(
            f"{row['NombreCliente']} (Ciudad: {row['Ciudad']}): "
            f"{row['total_unidades']} unidades, "
            f"${row['total_ingresos']} gastados. "
            f"Productos: {row['productos']}. "
            f"Categorías: {row['categorias']}."
        )

    cliente_totales_text = (
            "Ventas totales por cliente (resumen global):\n" +
            "\n".join(lines_cliente)
    )

    docs.append(Document(
        page_content=cliente_totales_text,
        metadata={"tipo": "cliente_totales_global"}
    ))

    return docs
