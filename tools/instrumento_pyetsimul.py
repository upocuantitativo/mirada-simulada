"""Calcula con PyEtSimul el error de medida de tres montajes de eye-tracker y lo guarda en data/instrumento.json.

La app web aplica esa tabla como capa opcional: "qué registraría un aparato si la persona mirase ahí".
PyEtSimul simula el aparato (ojo, cámara, luz, calibración), no dónde mira la gente.

Uso:  pip install pyetsimul  &&  python tools/instrumento_pyetsimul.py
Los valores de ruido y de movimiento de cabeza de MONTAJES son supuestos didácticos, no medidas de un aparato comercial.
"""
import json, math, os
import numpy as np
from pyetsimul.camera_noise import GlintNoiseConfig
from pyetsimul.core import Camera, Eye, Light
from pyetsimul.core.eye_model import get_eye_model
from pyetsimul.evaluation.gaze_accuracy import evaluate_gaze_accuracy
from pyetsimul.gaze_mapping.polynomial import PolynomialGazeModel
from pyetsimul.simulation import DataGenerationStrategy, EyePositionVariation, TargetPositionVariation
from pyetsimul.types import Position3D

# PyEtSimul 5.1.0 pide serialize() a la configuración de ruido, pero la clase no lo define
if not hasattr(GlintNoiseConfig, 'serialize'):
    GlintNoiseConfig.serialize = lambda self: dict(vars(self))

W, H = 380.0, 300.0      # pantalla simulada, mm
DIST = 700.0             # distancia ojo-pantalla, mm
NX, NZ = 9, 7            # rejilla de puntos de mirada
HW, HH = .88 * W / 2, .83 * H / 2
HV9 = [Position3D(float(x), 0.0, float(z)) for x, z in
       [(0, 0), (0, HH), (0, -HH), (-HW, 0), (HW, 0), (-HW, HH), (HW, HH), (-HW, -HH), (HW, -HH)]]
MONTAJES = [
    # clave, nombre, ruido del reflejo corneal (px de cámara), holgura de cabeza (mm)
    ('laboratorio', 'Laboratorio: cabeza fija y luz controlada', 0.05, 0),
    ('oficina', 'Oficina: la cabeza se mueve unos centímetros', 0.25, 20),
    ('campo', 'Campo: poca luz y persona que se mueve', 0.75, 45),
]


def generar(tracker, eye, cam, luz, variacion, nombre):
    gen = DataGenerationStrategy(eyes=[eye], cameras=[cam], lights=[luz], gaze_target=Position3D(0.0, 0.0, 0.0),
                                 experiment_name=nombre, save_to_file=False, use_refraction=tracker.use_refraction)
    return evaluate_gaze_accuracy(eye_tracker=tracker, dataset=gen.execute(variacion), description=nombre)


def medir(clave, nombre, ruido, cabeza):
    eye = Eye(model=get_eye_model('PyEtSimul'))
    eye.position = Position3D(0.0, DIST, 50.0)
    cam0 = Camera(); cam0.position = Position3D(0.0, 350.0, -150.0); cam0.point_at(eye.position)
    luz = Light(position=Position3D(70.0, 350.0, -140.0))
    tracker = PolynomialGazeModel.create(cameras=[cam0], lights=[luz], calib_points=HV9, polynomial='cerrolaza_2008_symmetric')
    tracker.run_calibration(eye)
    cam = Camera(glint_noise_config=GlintNoiseConfig(noise_type='gaussian', std=ruido, seed=2026))
    cam.position = cam0.position; cam.point_at(eye.position)
    pant = TargetPositionVariation(grid_center=Position3D(0.0, 0.0, 0.0), dx=[-W / 2, W / 2], dy=[0.0, 0.0],
                                   dz=[-H / 2, H / 2], grid_size=[NX, 1, NZ])
    r = generar(tracker, eye, cam, luz, pant, clave + '_pantalla')
    ang = [a for a in r.errors_angular if a is not None and not math.isnan(a)]
    sesgo = []
    for p, g in zip(r.predicted_points, r.ground_truth_points):
        if p is None: continue
        sesgo.append(dict(x=round(g.x / W + .5, 3), y=round(.5 - g.z / H, 3), dx=round((p.x - g.x) / W, 4), dy=round(-(p.z - g.z) / H, 4)))
    cab = 0.0
    if cabeza:
        obs = EyePositionVariation(center=eye.position, dx=[-cabeza, cabeza], dy=[-cabeza, cabeza], dz=[0.0, 0.0], grid_size=[5, 5, 1])
        rc = generar(tracker, eye, cam, luz, obs, clave + '_cabeza')
        vals = [a for a in rc.errors_angular if a is not None and not math.isnan(a)]
        cab = float(np.mean(vals))
    return dict(clave=clave, nombre=nombre, ruido_px=ruido, cabeza_mm=cabeza, puntos=len(ang),
                error_medio_deg=round(float(np.mean(ang)), 3), error_p95_deg=round(float(np.percentile(ang, 95)), 3),
                error_cabeza_deg=round(cab, 3), sesgo=sesgo)


if __name__ == '__main__':
    salida = dict(fuente='PyEtSimul 5.1.0 (Böhme et al., 2008; GPL-3.0). Generado con tools/instrumento_pyetsimul.py',
                  aviso='Supuestos didácticos de ruido y cabeza; no son especificaciones de un aparato comercial.',
                  pantalla_mm=[W, H], distancia_mm=DIST, grados_por_ancho=round(2 * math.degrees(math.atan(W / 2 / DIST)), 2),
                  montajes=[medir(*m) for m in MONTAJES])
    dest = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'instrumento.json')
    with open(dest, 'w', encoding='utf-8') as f:
        json.dump(salida, f, ensure_ascii=False, separators=(',', ':'))
    for m in salida['montajes']:
        print(m['clave'], m['error_medio_deg'], m['error_p95_deg'], m['error_cabeza_deg'], m['puntos'])
