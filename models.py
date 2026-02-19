from datetime import datetime
from pydantic import BaseModel


class LineaRequest(BaseModel):
    c_articulo: str
    c_tamanio: str
    c_cuenta: int = 0
    q_articulo: float
    m_unit_impreso: float
    m_impuest_neto: float
    m_prec_venta: float
    pc_desc_uno: float = 0.0
    pc_desc_dos: float = 0.0
    m_desc_total: float = 0.0


class CabeceraRequest(BaseModel):
    c_cliente: int
    f_factura: datetime
    q_total_de_ar: float
    m_basico_grav: float
    m_basic_total: float
    m_descuento: float = 0.0
    descuento: float = 0.0
    m_impuesto: float
    m_total: float


class ComprobanteRequest(BaseModel):
    observaciones: str  # Formato: "RUT | Nombre cliente | Comprobante plataforma"
    cabecera: CabeceraRequest
    lineas: list[LineaRequest]


class ComprobanteResponse(BaseModel):
    id: int
    r_comproban: int
    lineas_insertadas: int
