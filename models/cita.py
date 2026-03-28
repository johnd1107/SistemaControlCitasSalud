class Cita:
    def __init__(self, id_cita, id_paciente, id_medico, fecha_cita, motivo, estado='Programada'):
        self.id_cita = id_cita
        self.id_paciente = id_paciente
        self.id_medico = id_medico
        self.fecha_cita = fecha_cita
        self.motivo = motivo
        self.estado = estado