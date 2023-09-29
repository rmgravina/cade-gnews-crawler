import sqlite3
from datetime import date

def conect_db():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    return c, conn


def create_tables():
    c, conn = conect_db()
    c.executescript("""CREATE TABLE IF NOT EXISTS noticias_db (titulo TEXT,
              noticia TEXT,
              fonte TEXT); CREATE TABLE IF NOT EXISTS buscas_db (busca TEXT,
              dia TEXT);""")
    conn.commit()


def insert_query(query, dia):
    c, conn = conect_db()
    c.execute("""
    INSERT INTO buscas_db (busca, dia)
    VALUES (?,?)""",
    (query, dia)).rowcount

    conn.commit()

def get_dia():
    c, conn = conect_db()
    dias = []
    for row in c.execute("SELECT * FROM buscas_db"):
        dias.append(row[1])
    return dias

def get_busca(dia_filtro):
    c, conn = conect_db()
    buscas_anteriores = []
    for row in c.execute("SELECT * FROM buscas_db WHERE dia = ?", (dia_filtro,)):
        buscas_anteriores.append(row[0])
    return buscas_anteriores


def select_titulo():
    c, conn = conect_db()
    titulos = []
    for row in c.execute("SELECT * FROM noticias_db"):
        titulos.append(row[0])
    return titulos

def select_noticias():
    c, conn = conect_db()
    noticias = []
    for row in c.execute("SELECT * FROM noticias_db"):
        noticias.append(row[1])
    return noticias


def inserir_noticias(titulo, noticia, fonte):
    c, conn = conect_db()
    if titulo in select_titulo():
        
        return "Notícia já cadastrada"
    
    else:
            
        c.execute("""
        INSERT INTO noticias_db (titulo, noticia, fonte)
        VALUES (?,?,?)""",
        (titulo, noticia, fonte)).rowcount

    conn.commit()