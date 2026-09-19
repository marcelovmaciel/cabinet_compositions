# Follow-up: Defense succession and three vacancy actors

This research directory contains source copies and proposed adjudications. It does not modify canonical inputs, releases, electoral inputs, or manuscript files.

## Supported adjudication

Braga Netto's effective service as Defense minister begins **2021-03-30**. Preserve the signed possession term dated **2021-04-01** as a distinct administrative date. The official March 30 commanders-succession meeting, an official ministerial audience that afternoon, and contemporaneous reporting of his substantive redirection of a Defense policy statement jointly establish actual exercise after publication of his appointment. This is stronger than an isolated signature. See `defense_adjudication.json`, `defense_sources.json`, and the two saved official HTML pages.

Proposed exact input change: move `service-jair_bolsonaro-0-19` from April 1 to March 30; remove `gap-C049-defense`; retain the April 1 possession evidence and explicit date-semantics uncertainty. No new affiliation spell is required for Braga Netto. This resolves that office-occupancy dependency, not necessarily every aggregate unknown on those dates.

## Unresolved personal affiliation dependencies

| Person | Vacancy service interval [start,end) | Result |
| --- | --- | --- |
| Renato de Lima França | 2020-04-28 to 2020-04-29 | No affirmative party or explicit non-affiliation statement recovered. Official career biography does not establish party membership. |
| Luiz Pontel de Souza | 2020-04-24 to 2020-04-29 | No affirmative party or explicit non-affiliation statement recovered. Theophilo's announced PSDB departure cannot be assigned to Pontel. |
| Otávio Brandelli | 2021-03-30 to 2021-04-06 | No affirmative party or explicit non-affiliation statement recovered. Full 2021 Senate hearing, nomination papers, official biography, and contemporaneous reporting do not establish personal party status. |

The existing vacancy-service assertions were inspected. Continuing secretaries' careers, office nominations, sponsorship, or apparent neutrality were not converted into non-affiliation.

### Rejected apparent affiliation evidence

- The May 2022 archived English Wikipedia cabinet/team table gives Pontel a dash. The same table gives dashes to people with documented affiliations, including Salim Mattar and Marcos Cintra. There is no reliable explicit non-affiliation convention. `english_cabinet_202205.html` preserves this table.
- December 2018 reporting places Guilherme Theophilo's PSDB departure near discussion of Pontel's appointment. Its subject is Theophilo, not Pontel.
- The December 2018 Brandelli column labels an allegation that he was a PT member as diplomatic rumor based on his earlier appointment by Mercadante. It supplies neither a reliable membership assertion nor a departure date. It does not justify enumerating PT and non-affiliation as exhaustive alternatives.
- “Sem partido” in 2021 reports of Brandelli's appointment modifies President Bolsonaro. “Independent” in an SSRN author result is an institutional author affiliation, not political-party status.
- Renato França references to “filiado” in professional-association reporting concern association membership or a different named person, not a political party.

### Additional office-date lead not promoted

A March 31, 2021 Exame report says incoming Foreign minister Carlos França had already redirected Itamaraty staff. That is a useful lead but has not been corroborated by the multiple dated actual-exercise sources supporting the Defense adjudication. It is insufficient by itself to delete Brandelli's vacancy spell. The April 6 possession evidence remains retained. The FUNAG biography gives an appointment date inconsistent by one day with the DOU; it does not prove earlier effective exercise.

## Public TSE list investigation

`tse_scan_summary.json` records the completed scan of **39 party identities in seven municipalities (273 successful queries, no errors)**. Targeted exact names and accent-normalized variants include these three people and the other current research blockers. The municipalities were selected from documented birth, study, and career locations: Garibaldi, Sananduva, Porto Alegre, Presidente Prudente, Londrina, Campo Grande, and Boa Vista. There were **no matches**. Only scoped target matches would have been retained; unrelated citizens' raw registry records were not saved.

The current public official-party-list endpoint cannot turn this negative finding into non-affiliation. The TSE's own manual expressly permits a regularly affiliated voter to be absent from a party's last official list (section 5.1, printed page 7). Moreover, a current list can omit past cancelled affiliations. `tse_consulta_manual.pdf` and `.txt` preserve the official documentation. A party-only departure can also leave a cancellation pending in the registry; an apparent REGULAR status must therefore be considered alongside an exit field rather than mechanically overriding it.

## Principal sources inspected

- Official Defense commanders-succession note, March 30, 2021: https://www.gov.br/defesa/pt-br/centrais-de-conteudo/noticias/substituicao-dos-comandantes-das-forcas
- Official military-ordinariate agenda, March 30, 2021: https://www.gov.br/defesa/pt-br/acesso-a-informacao/agenda-de-autoridades/ordinariado-militar-do-brasil/2021-03-30
- Folha contemporaneous account of Braga Netto's first substantive ministerial acts: https://www1.folha.uol.com.br/poder/2021/03/braga-netto-alterou-ordem-do-dia-sobre-golpe-de-1964-e-excluiu-mencao-de-forcas-como-instituicao-de-estado.shtml
- Defense nomination/dismissal publication: https://static.poder360.com.br/2021/03/DOU-ministerio-defesa-exoneracao-fernando-azevedo-nomeacao-braga-netto.pdf
- Signed Defense possession term, retained by the parent researcher: https://www.camara.leg.br/proposicoesWeb/prop_mostrarintegra?codteor=1990585&filename=REC+9%2F2021
- Renato França official CV: https://www.gov.br/secretariageral/pt-br/centrais-de-conteudo/curriculos/subchefia-para-assuntos-juridicos/RENATOFRANA.pdf
- Pontel/Theophilo appointment reporting: https://noticias.uol.com.br/politica/ultimas-noticias/2018/12/04/moro-anuncia-delegado-da-pf-para-ser-o-numero-2-e-general-para-secretaria.htm
- Archived English cabinet table: https://browse.zim.carpocratian.org/content/wikipedia_en_all_maxi_2022-05/A/Bolsonaro_administration_cabinet_members
- Brandelli Senate hearing, July 6, 2021: https://www25.senado.leg.br/web/atividade/notas-taquigraficas/-/notas/r/10023
- Brandelli Senate nomination file: https://www25.senado.leg.br/web/atividade/materias/-/materia/148752
- Brandelli official biography: https://www.gov.br/funag/pt-br/chdd/historia-diplomatica/secretarios-gerais-das-relacoes-exteriores/otavio-brandelli
- Foreign-ministry March 31 lead: https://exame.com/bussola/itamaraty-mais-pragmatico-busca-novos-mercados-para-o-brasil-no-exterior/
- TSE consultation manual: https://filia2-consulta.tse.jus.br/assets/GUS_FILIA_Consulta.pdf

No primary party-set completion is claimed from the three unresolved personal records. Neither absent fields nor failed searches have been replaced with “Sem partido.”
