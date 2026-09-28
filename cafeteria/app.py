from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# Configuración de conexión a MySQL
db_config = {
    'host': 'localhost',
    'user': 'root',           
    'password': 'root',      
    'database': 'cafeteria_universitaria'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/')
def index():
    # 5. Página principal
    return render_template('index.html')

@app.route('/productos')
def productos():
    # 6. Página de productos
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM producto")
    lista_productos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('productos.html', productos=lista_productos)

@app.route('/pedidos')
def pedidos():
    # 7. Página de pedidos mostrando los totales
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT p.id_pedido, c.nombre AS cliente, p.estado, 
               COALESCE(SUM(dp.cantidad * dp.precio_unitario), 0) AS total
        FROM pedido p
        JOIN cliente c ON p.id_cliente = c.id_cliente
        LEFT JOIN detalle_pedido dp ON p.id_pedido = dp.id_pedido
        GROUP BY p.id_pedido, c.nombre, p.estado;
    """
    cursor.execute(query)
    lista_pedidos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('pedidos.html', pedidos=lista_pedidos)

@app.route('/agregar_producto', methods=['GET', 'POST'])
def agregar_producto():
    # 8. Página para agregar un nuevo producto
    if request.method == 'POST':
        nombre = request.form['nombre']
        categoria = request.form['categoria']
        precio = request.form['precio']
        stock = request.form['stock']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO producto (nombre, categoria, precio, stock) VALUES (%s, %s, %s, %s)",
                       (nombre, categoria, precio, stock))
        conn.commit()
        cursor.close()  
        conn.close()        
        return redirect(url_for('productos'))
    
    return render_template('agregar_producto.html')

@app.route('/actualizar_producto/<int:id>', methods=['GET', 'POST'])
def actualizar_producto(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        nuevo_nombre = request.form['nombre']
        nueva_categoria = request.form['categoria']
        nuevo_precio = request.form['precio']
        nuevo_stock = request.form['stock']

        cursor.execute("""
            UPDATE producto 
            SET nombre = %s, categoria = %s, precio = %s, stock = %s 
            WHERE id_producto = %s
        """, (nuevo_nombre, nueva_categoria, nuevo_precio, nuevo_stock, id))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return redirect(url_for('productos'))

    else:
        cursor.execute("SELECT * FROM producto WHERE id_producto = %s", (id,))
        producto_actual = cursor.fetchone()
        
        cursor.close()
        conn.close()

        return render_template('actualizar_producto.html', producto=producto_actual)



@app.route('/agregar_pedido', methods=['GET', 'POST'])
def agregar_pedido():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        # Recibe los datos del formulario
        id_cliente = request.form['id_cliente']
        estado = request.form['estado']
        
        # Inserta el nuevo pedido
        cursor.execute("INSERT INTO pedido (id_cliente, estado) VALUES (%s, %s)", (id_cliente, estado))
        conn.commit()
        
        cursor.close()
        conn.close()
        return redirect(url_for('pedidos'))

    else:
        # Si es GET, consultamos los clientes para llenar el <select> en el HTML
        cursor.execute("SELECT id_cliente, nombre FROM cliente")
        lista_clientes = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return render_template('agregar_pedido.html', clientes=lista_clientes)


@app.route('/actualizar_pedido/<int:id>', methods=['GET', 'POST'])
def actualizar_pedido(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        # Solo actualizamos el estado, el cliente no cambia
        nuevo_estado = request.form['estado']

        cursor.execute("UPDATE pedido SET estado = %s WHERE id_pedido = %s", (nuevo_estado, id))
        conn.commit()
        
        cursor.close()
        conn.close()
        return redirect(url_for('pedidos'))

    else:
        # Hacemos un JOIN para mostrar el nombre del cliente junto con la información del pedido
        query = """
            SELECT p.id_pedido, p.estado, c.nombre AS cliente
            FROM pedido p
            JOIN cliente c ON p.id_cliente = c.id_cliente
            WHERE p.id_pedido = %s
        """
        cursor.execute(query, (id,))
        pedido_actual = cursor.fetchone()
        
        cursor.close()
        conn.close()

        return render_template('actualizar_pedido.html', pedido=pedido_actual)



@app.route('/borrar_producto/<int:id>')
def borrar_producto(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Eliminar registros en detalle_pedido para evitar errores de clave foránea
    cursor.execute("DELETE FROM detalle_pedido WHERE id_producto = %s", (id,))
    # 2. Eliminar el producto
    cursor.execute("DELETE FROM producto WHERE id_producto = %s", (id,))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for('productos'))

@app.route('/borrar_pedido/<int:id>')
def borrar_pedido(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Eliminar los detalles asociados al pedido
    cursor.execute("DELETE FROM detalle_pedido WHERE id_pedido = %s", (id,))
    # 2. Eliminar el pedido
    cursor.execute("DELETE FROM pedido WHERE id_pedido = %s", (id,))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for('pedidos'))        



if __name__ == '__main__':
    # 4. Servidor Flask ejecutándose
    app.run(debug=True)