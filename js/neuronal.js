/* MSI-Net (Kroner et al., 2020; MIT) en el navegador. Se carga solo si se pide.
   Predice la saliencia general: no distingue audiencias y se entrenó con fotografías (SALICON). */
(function () {
  let modelo = null, tfListo = null;
  function cargarTF() {
    if (tfListo) return tfListo;
    tfListo = new Promise((ok, mal) => { const s = document.createElement('script'); s.src = 'https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@1.1.2'; s.onload = ok; s.onerror = () => { tfListo = null; mal(new Error('tfjs')); }; document.head.append(s); });
    return tfListo;
  }
  async function predecir(lienzo, ancho, alto) {
    await cargarTF();
    if (!modelo) modelo = await tf.loadGraphModel('modelos/msi-net/model.json');
    const dims = [240, 320];
    const salida = tf.tidy(() => {
      const x = tf.clipByValue(tf.image.resizeBilinear(tf.browser.fromPixels(lienzo).toFloat().expandDims(), dims, true), 0, 255);
      return tf.clipByValue(modelo.predict(x), 0, 255).squeeze();
    });
    const [h, w] = salida.shape, datos = await salida.data(); salida.dispose();
    return Motor.desdeRejilla(Float32Array.from(datos), w, h, ancho, alto);
  }
  window.Neuronal = { predecir };
})();
