# Proyecto Dietética: Backend, Frontend y Orquestación

Este proyecto consta de tres componentes principales desplegables mediante Docker:
1. **Frontend** (Next.js): La interfaz de usuario.
2. **API de Productos** (FastAPI): Gestión de productos y categorías.
3. **API de Stock** (Django): Gestión de stock e inventario.

## 1. Estructura del Proyecto

```
.
├── backend_productos/       # API de Productos (FastAPI)
│   ├── app/
│   ├── requirements.txt
│   └── Dockerfile
├── backend_stock/         # API de Stock (Django)
│   ├── app/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                # Aplicación Next.js
│   ├── app/
│   ├── package.json
│   └── Dockerfile
├── nginx/                   # Configuración de Nginx
│   └── nginx.conf
├── docker-compose.yml       # Orquestación de todos los servicios
└── README.md
```

## 2. Despliegue y Ejecución

### 2.1 Requisitos Previos
- Docker instalado y funcionando.
- Docker Compose instalado.

### 2.2 Pasos para el Despliegue

1. **Navegar al directorio raíz** del proyecto:
   ```bash
   cd /ruta/a/tu/proyecto
   ```

2. **Construir y ejecutar los contenedores**:
   Ejecuta el siguiente comando desde el directorio que contiene el `docker-compose.yml`:

   ```bash
   docker-compose up --build -d
   ```

   - `--build`: Fuerza la reconstrucción de las imágenes (útil si has hecho cambios en el código).
   - `-d`: Ejecuta los contenedores en segundo plano (detached mode).

### 2.3 Acceso a las Aplicaciones

Una vez que los contenedores estén corriendo, puedes acceder a las aplicaciones a través de los siguientes puertos en tu máquina:

- **Frontend (Next.js)**: [http://localhost:3000](http://localhost:3000)
- **API de Productos (FastAPI)**: [http://localhost:8000](http://localhost:8000)
- **API de Stock (Django)**: [http://localhost:8001](http://localhost:8001)
- **Nginx (Proxy Inverso)**: [http://localhost:8092](http://localhost:8092)

## 3. Configuración de Redes y Comunicación

### 3.1 Red Docker (`dietetica-network`)
Todos los servicios están conectados a una red Docker común llamada `dietetica-network`. Esto permite que los contenedores se comuniquen entre sí utilizando los nombres de los servicios como nombres de host.

### 3.2 Comunicación entre Servicios

- **Frontend → Backend**: La aplicación Next.js se comunica con las APIs utilizando los nombres de los servicios definidos en `docker-compose.yml`:
  - Productos: `http://backend_productos:8000`
  - Stock: `http://backend_stock:8000`

- **Nginx → Backend**: El proxy inverso Nginx reenvía las peticiones a los servicios correspondientes:
  - `/productos/` → `http://backend_productos:8000/`
  - `/stock/` → `http://backend_stock:8000/`

## 4. Gestión de Volúmenes y Datos

### 4.1 Datos Persistentes
Los datos de las bases de datos se almacenan en volúmenes Docker persistentes para que no se pierdan al reiniciar los contenedores:
- `postgres_data`: Datos de la base de datos PostgreSQL (para ambas APIs).

### 4.2 Archivos Estáticos
Los archivos estáticos (imágenes, CSS, JS) servidos por Nginx se almacenan en:
- `media_files`: Para archivos subidos por los usuarios (imágenes de productos).
- `static_files`: Para archivos estáticos de la aplicación.

## 5. Administración de Servicios

### 5.1 Detener los Servicios
Para detener los contenedores sin eliminar los volúmenes:
```bash
docker-compose down
```

Para detener y eliminar los volúmenes (y por lo tanto, borrar todos los datos):
```bash
docker-compose down -v
```

### 5.2 Ver Logs
Para ver los logs de todos los servicios:
```bash
docker-compose logs -f
```

Para ver logs de un servicio específico:
```bash
docker-compose logs -f backend_productos
```

## 6. Configuración Adicional

### 6.1 Archivos de Configuración
- **`docker-compose.yml`**: Define la infraestructura, redes y volúmenes.
- **`nginx/nginx.conf`**: Configuración del servidor web Nginx, incluyendo proxy inverso y servir archivos estáticos.
- **Archivos `Dockerfile`**: Específicos para cada componente, definen cómo construir cada imagen.

### 6.2 Personalización
Para modificar la configuración de Nginx, edita `nginx/nginx.conf`. Para cambiar puertos, volúmenes o servicios, edita `docker-compose.yml`. Para modificar las aplicaciones, edita los directorios correspondientes (`backend_productos/`, `backend_stock/`, `frontend/`).

## 7. Notas de Desarrollo

- **Ambiente de Desarrollo**: Los archivos de configuración están optimizados para desarrollo local.
- **Producción**: Para producción, se recomienda configurar variables de entorno, certificados SSL para Nginx y considerar un orquestador más robusto como Docker Swarm o Kubernetes.