from enum import Enum


TIPO_USUARIO: dict[str, str] = {
    'Administrador': 'Administrador',
    'Supervisor': 'Supervisor',
    'Colaborador': 'Colaborador',
}


CATEGORIA_EPI: dict[str, str] = {
    "Proteção Respiratória": "Máscaras PFF2, respiradores com filtros",
    "Proteção Auditiva": "Protetores auriculares, abafadores de som",
    "Proteção Ocular e Facial": "Óculos de proteção, viseiras, protetores faciais",
    "Proteção das Mãos e Braços": "Luvas de segurança, luvas de proteção química",
    "Proteção dos Pés e Pernas": "Botas de segurança, sapatos com biqueira de aço",
    "Proteção do Corpo": "Aventais, coletes à prova de balas, uniformes de proteção contra produtos químicos",
    "Proteção Contra Queda": "Cintos de segurança, cordas de segurança, talabartes"
}


CARGOS: dict[str, str] = {
    "Gerente": "Gerente",
    "Pedreiro": "Pedreiro",
    "Gerente de Operações": "Gerente de Operações",
    "Coordenador de Vendas": "Coordenador de Vendas",
    "Analista de Logística": "Analista de Logística",
    "Técnico de Manutenção": "Técnico de Manutenção",
}

class Status(Enum):

    EMPRESTADO: str = "Emprestado"
    EM_USO:     str = "Em Uso"
    FORNECIDO:  str = "Fornecido"
    DEVOLVIDO:  str = "Devolvido"
    DANIFICADO: str = "Danificado"
    PERDIDO:    str = "Perdido"


    @classmethod
    def choices(cls):
        return [(tag.name, tag.value) for tag in cls]
    

    @classmethod
    def obter_status_para_cadastro(cls):
        return [
            (cls.EMPRESTADO.name, cls.EMPRESTADO.value),
            (cls.EM_USO.name, cls.EM_USO.value),
            (cls.FORNECIDO.name, cls.FORNECIDO.value),
        ]
