struct VertexOutput {
    float4 position : SV_Position;
    float2 uv : TEXCOORD0;
};

VertexOutput vertex_main(uint id : SV_VertexID) {
    const float2 positions[3] = { float2(-1, -1), float2(3, -1), float2(-1, 3) };
    VertexOutput output;
    output.position = float4(positions[id], 0, 1);
    output.uv = float2(positions[id].x * 0.5 + 0.5, 0.5 - positions[id].y * 0.5);
    return output;
}

float4 fragment_main(VertexOutput input) : SV_Target0 {
    if (input.uv.y < 0.5) {
        if (input.uv.x < 0.5) return float4(1, 0, 0, 0.5);
        return float4(0, 1, 0, 0.75);
    }
    if (input.uv.x < 0.5) return float4(0, 0, 1, 0.25);
    return float4(0.125, 0.25, 0.5, 1);
}

float4 overlay_main(VertexOutput input) : SV_Target0 {
    return float4(1, 0, 1, 1);
}
