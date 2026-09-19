# Official TSE schema evidence

Read-only public artifacts retrieved from filia2-externo.tse.jus.br; no login, protected record API or modification was used.

1. `main.655678f4759dcc30.js`: module 6758 defines `A_PEDIDO_ELEITOR=2`, `EXPULSAO=1`, `JUDICIAL=10`; label mapping for the first is `A pedido do eleitor`. The public pipe `motivoDesfiliacaoPipe` transforms its argument through that module's mapping.
2. `672.9e4193a1e7e92416.js`: record template displays `registro.cdMotivoDesfiliacao | motivoDesfiliacaoPipe`, `registro.dtDesfiliacao` and `registro.tsCadastroDesfiliacao` as separate fields.
3. Same chunk, module 6559: selectable reasons contain value 2/label A pedido do eleitor. The form assigns `i.dtDesfiliacao=this.formDesfiliar.controls.data.value` and `i.cdMotivoDesfiliacao=this.formDesfiliar.controls.motivo.value`. Its `msgStatus(i){2==i?...}` clause explicitly distinguishes elector notification to the court from party notification under other reasons. The function was inspected, not called.
4. `927.95ca5669143d8c8c.js`: `habilitaReverter` accepts REGULAR plus COM_PENDENCIA. `tsCadastroDesfiliacao` is independently converted for display. Pending and affiliation status are not the same variable.
5. Chunk 672 module 3333: `SEM_PENDENCIA="0"`, `COM_PENDENCIA="1"`; module 3713: `EXTERNO="1"`, `INTERNO="0"`. These origin enum labels alone do not prove an individual's historical actor or migration path.

Inference bounded to current client semantics: the retained reason is unambiguously a request category; a populated departure date can be part of the party's pending workflow. Historical effective termination and legacy migration of the null timestamp remain unresolved. Preserve the original individual row and both supported December 2022 alternatives.
