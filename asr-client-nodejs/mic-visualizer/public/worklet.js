class PCMWorklet extends AudioWorkletProcessor {
  process(inputs) {
    const input = inputs[0][0];
    if (!input) return true;

    const pcm = new Int16Array(input.length);
    for (let i = 0; i < input.length; i++) {
      const s = Math.max(-1, Math.min(1, input[i]));
      pcm[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
    }

    // Send Int16Array for gRPC
    this.port.postMessage({ type: "pcm", data: pcm.buffer }, [pcm.buffer]);

    // Also send Float32Array for drawing (copy)
    this.port.postMessage({ type: "raw", data: Float32Array.from(input).buffer }, [Float32Array.from(input).buffer]);

    return true;
  }
}
registerProcessor('pcm-worklet', PCMWorklet);

