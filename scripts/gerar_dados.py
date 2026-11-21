import numpy as np
import pandas as pd
from pathlib import Path

SEED = 7
rng = np.random.default_rng(SEED)
OUT = Path(__file__).resolve().parents[1] / "data" / "raw"
OUT.mkdir(parents=True, exist_ok=True)

INICIO, FIM = pd.Timestamp("2026-07-01"), pd.Timestamp("2026-10-31")
dias = pd.date_range(INICIO, FIM, freq="D")
ND = len(dias)

fcs = pd.DataFrame({
    "fc_id": ["SP01", "MG01", "BA01"],
    "nome_fc": ["FC São Paulo 01", "FC Minas Gerais 01", "FC Bahia 01"],
    "uf": ["SP", "MG", "BA"],
    "inicio_operacao": ["2019-03-01", "2021-08-15", "2023-05-10"],
})
FC = fcs["fc_id"].tolist()
peso_fc = np.array([0.55, 0.28, 0.17])
linhas_dia_fc = np.array([1150, 580, 360])
uph_pick = {"SP01": 96, "MG01": 89, "BA01": 74}
uph_pack = {"SP01": 118, "MG01": 110, "BA01": 95}
uph_exp = {"SP01": 260, "MG01": 240, "BA01": 210}
uph_rec = {"SP01": 240, "MG01": 225, "BA01": 190}
uph_arm = {"SP01": 125, "MG01": 118, "BA01": 98}
p_div_fc = {"SP01": 0.035, "MG01": 0.05, "BA01": 0.09}
p_rupt_fc = {"SP01": 0.004, "MG01": 0.006, "BA01": 0.013}
p_erro_fc = {"SP01": 0.0018, "MG01": 0.0025, "BA01": 0.0045}

cats = {
    "Celulares e Smartphones": dict(p=0.06, preco=(600, 4500), tam="P", risco=2.2, pop=1.3),
    "Informática":             dict(p=0.08, preco=(80, 3500),  tam="M", risco=1.8, pop=1.0),
    "Eletrônicos, Áudio e Vídeo": dict(p=0.09, preco=(60, 2500), tam="M", risco=1.5, pop=1.1),
    "Casa, Móveis e Decoração": dict(p=0.14, preco=(25, 900),  tam="G", risco=0.6, pop=0.9),
    "Beleza e Cuidado Pessoal": dict(p=0.12, preco=(15, 350),  tam="P", risco=1.6, pop=1.2),
    "Esportes e Fitness":      dict(p=0.09, preco=(30, 1200),  tam="M", risco=0.8, pop=0.8),
    "Brinquedos e Hobbies":    dict(p=0.08, preco=(20, 600),   tam="M", risco=0.8, pop=0.8),
    "Ferramentas":             dict(p=0.08, preco=(25, 1500),  tam="M", risco=1.0, pop=0.8),
    "Pet Shop":                dict(p=0.08, preco=(20, 400),   tam="G", risco=0.5, pop=1.0),
    "Calçados, Roupas e Bolsas": dict(p=0.11, preco=(40, 600), tam="P", risco=1.0, pop=1.0),
    "Eletrodomésticos":        dict(p=0.07, preco=(90, 3200),  tam="GG", risco=0.5, pop=0.7),
}
cat_nomes = list(cats)

N_SELLER = 620
pref = ["Loja", "Mega", "Casa", "Top", "Prime", "Shop", "Brasil", "Express", "Mix", "Center", "Point", "Store"]
suf = ["Digital", "Imports", "Utilidades", "Tech", "Varejo", "Commerce", "Distribuidora", "Online", "Outlet", "Plus"]
sellers = pd.DataFrame({
    "seller_id": [f"SL{100000 + i}" for i in range(N_SELLER)],
    "nome_fantasia": [f"{rng.choice(pref)} {rng.choice(suf)} {i:03d}" for i in range(N_SELLER)],
    "reputacao": rng.choice(["verde", "verde claro", "amarelo", "laranja"], N_SELLER, p=[0.62, 0.23, 0.11, 0.04]),
    "inicio_full": [(pd.Timestamp("2020-01-01") + pd.Timedelta(days=int(d))).date() for d in rng.integers(0, 2300, N_SELLER)],
})
cat_seller = rng.choice(cat_nomes, N_SELLER, p=[v["p"] for v in cats.values()])

N_SKU = 4200
seller_idx = rng.choice(N_SELLER, N_SKU, p=(w := rng.pareto(1.3, N_SELLER) + 1) / w.sum())
cat_sku = np.where(rng.random(N_SKU) < 0.8, cat_seller[seller_idx], rng.choice(cat_nomes, N_SKU))
preco = np.array([round(np.exp(rng.uniform(np.log(cats[c]["preco"][0]), np.log(cats[c]["preco"][1]))), 2) for c in cat_sku])
fc_sku = rng.choice(3, N_SKU, p=peso_fc)
pop = (rng.pareto(1.15, N_SKU) + 0.05) * np.array([cats[c]["pop"] for c in cat_sku])
lento = rng.random(N_SKU) < 0.12
pop[lento] *= 0.03
adj = ["Kit", "Original", "Premium", "Pro", "Compacto", "Lançamento", "Reforçado", "Slim", "Max", "Básico"]
skus = pd.DataFrame({
    "inventory_id": [f"INV{rng.integers(10**7, 10**8)}{i:04d}" for i in range(N_SKU)],
    "seller_id": sellers["seller_id"].values[seller_idx],
    "titulo": [f"{c.split(',')[0].split(' e ')[0]} {rng.choice(adj)} {i:04d}" for i, c in enumerate(cat_sku)],
    "categoria": cat_sku,
    "tamanho": [cats[c]["tam"] for c in cat_sku],
    "preco_venda": preco,
    "fc_id": np.array(FC)[fc_sku],
})

def peso_hora():
    h = np.array([2, 1, 1, 1, 1, 2, 3, 4, 5, 6, 7, 7, 7, 6, 6, 6, 6, 7, 8, 9, 10, 10, 8, 5], float)
    return h / h.sum()
PH = peso_hora()

fator_dow = np.array([1.18, 1.08, 1.02, 1.0, 0.97, 0.85, 0.78])
picos = {}
for d in pd.date_range("2026-08-03", "2026-08-07"):
    picos[d] = (1.45, ["Ferramentas", "Eletrônicos, Áudio e Vídeo", "Esportes e Fitness", "Calçados, Roupas e Bolsas"])
for d in pd.date_range("2026-10-05", "2026-10-09"):
    picos[d] = (1.55, ["Brinquedos e Hobbies"])
picos[pd.Timestamp("2026-10-10")] = (1.9, cat_nomes)
picos[pd.Timestamp("2026-07-15")] = (1.5, cat_nomes)

COLETAS = [10, 14, 18, 22]
TURNOS = [("T1", 6, 14), ("T2", 14, 22)]

pedidos, apont, n_order = [], [], 0
saida_dia_fc = np.zeros((ND, 3))

for f, fc in enumerate(FC):
    idx_fc = np.nonzero(fc_sku == f)[0]
    ords = []
    for d, dt in enumerate(dias):
        mult, cats_pico = picos.get(dt, (1.0, []))
        lam = linhas_dia_fc[f] * fator_dow[dt.dayofweek] * (1 + 0.0004 * d)
        n = rng.poisson(lam * (1 + (mult - 1) * 0.35))
        w = pop[idx_fc].copy()
        if cats_pico:
            w = w * np.where(np.isin(cat_sku[idx_fc], cats_pico), mult * 1.6, 1.0)
        esc = rng.choice(idx_fc, n, p=w / w.sum())
        hora = rng.choice(24, n, p=PH) + rng.random(n)
        ts = dt + pd.to_timedelta(hora, unit="h")
        qtd = rng.choice([1, 1, 1, 1, 1, 1, 2, 2, 3, 4], n)
        for j in range(n):
            ords.append((ts[j], esc[j], qtd[j]))
    ords.sort(key=lambda x: x[0])
    arr = np.array([o[0] for o in ords], dtype="datetime64[ns]")
    sku_o = np.array([o[1] for o in ords])
    q_o = np.array([o[2] for o in ords])
    nO = len(ords)
    rnd = rng.random(nO)
    status = np.where(rnd < p_rupt_fc[fc], "CANCELADO_FALTA_ESTOQUE", np.where(rnd < p_rupt_fc[fc] + 0.008, "CANCELADO_CLIENTE", "EXPEDIDO"))
    fila = np.nonzero(status == "EXPEDIDO")[0]
    cum = np.cumsum(q_o[fila])
    t_pick = np.full(nO, np.datetime64("NaT", "ns"))
    turno_pick = np.full(nO, "", dtype=object)
    ptr, base_cum = 0, 0
    cap_base = linhas_dia_fc[f] * 1.7 * {"SP01": 1.0, "MG01": 0.96, "BA01": 0.95}[fc]
    for d, dt in enumerate(dias):
        mult, _ = picos.get(dt, (1.0, []))
        for tn, h0, h1 in TURNOS:
            ini, fim = dt + pd.Timedelta(hours=h0), dt + pd.Timedelta(hours=h1)
            share = 0.52 if tn == "T1" else 0.5
            cap = cap_base * share * rng.uniform(0.86, 1.04) * (0.62 if dt.dayofweek == 6 else 1.0) * (0.92 if mult > 1 else 1.0)
            uph = uph_pick[fc] * (0.95 if tn == "T2" else 1.0) * (0.9 if mult > 1 else 1.0) * rng.uniform(0.95, 1.05)
            elig_end = np.searchsorted(arr[fila], np.datetime64(fim - pd.Timedelta(minutes=20)))
            fila_u = (cum[elig_end - 1] - base_cum) if elig_end > ptr else 0
            cap += min(0.35 * cap, 0.5 * max(0, fila_u - 0.5 * cap))
            k = ptr
            limite_cum = base_cum + cap
            k_end = np.searchsorted(cum, limite_cum, side="right")
            k_end = min(k_end, elig_end)
            if k_end > ptr:
                sel = fila[ptr:k_end]
                frac = (cum[ptr:k_end] - base_cum) / cap
                t = np.datetime64(ini) + (frac * 8 * 3600e9).astype("timedelta64[ns]")
                t = np.maximum(t, arr[sel] + np.timedelta64(4, "m"))
                t = np.minimum(t, np.datetime64(fim) - np.timedelta64(15, "m"))
                t_pick[sel] = t
                turno_pick[sel] = tn
                unid = int(q_o[sel].sum())
                base_cum = cum[k_end - 1]
                ptr = k_end
            else:
                unid = 0
            for proc, u_ref in [("PICKING", uph), ("PACKING", uph_pack[fc] * uph / uph_pick[fc]), ("EXPEDICAO", uph_exp[fc] * uph / uph_pick[fc])]:
                horas = max(2.0, unid / u_ref * rng.uniform(1.0, 1.12))
                apont.append((dt.date(), fc, tn, proc, int(np.ceil(horas / 7.33)), round(horas, 2), unid))
            saida_dia_fc[d, f] += unid
    t_pack = t_pick + (rng.uniform(6, 45, nO) * 60e9).astype("timedelta64[ns]")
    tp = pd.to_datetime(t_pack)
    prox = []
    for t in tp:
        if pd.isna(t):
            prox.append(pd.NaT)
            continue
        hh = t.hour + t.minute / 60
        c = next((c for c in COLETAS if c > hh), None)
        prox.append(t.normalize() + pd.Timedelta(hours=c) if c else t.normalize() + pd.Timedelta(days=1, hours=COLETAS[0]))
    prox = pd.Series(prox)
    falha = {(d.date(), c): rng.random() < {"SP01": 0.03, "MG01": 0.06, "BA01": 0.05}[fc] for d in dias for c in COLETAS}
    for i in range(len(prox)):
        t = prox[i]
        while pd.notna(t) and falha.get((t.date(), t.hour), False):
            k = COLETAS.index(t.hour)
            t = t.normalize() + (pd.Timedelta(hours=COLETAS[k + 1]) if k + 1 < len(COLETAS) else pd.Timedelta(days=1, hours=COLETAS[0]))
        prox[i] = t
    arr_pd = pd.to_datetime(arr)
    limite = np.where(arr_pd.hour < 13, arr_pd.normalize() + pd.Timedelta(hours=18), arr_pd.normalize() + pd.Timedelta(days=1, hours=14))
    for i in range(nO):
        n_order += 1
        pedidos.append((f"MLO{2000000000 + n_order}", fc, skus["inventory_id"].iat[sku_o[i]], int(q_o[i]), arr_pd[i],
                        pd.Timestamp(limite[i]), pd.Timestamp(t_pick[i]) if status[i] == "EXPEDIDO" else pd.NaT,
                        tp[i] if status[i] == "EXPEDIDO" else pd.NaT, prox[i] if status[i] == "EXPEDIDO" else pd.NaT, status[i]))

pedidos = pd.DataFrame(pedidos, columns=["order_id", "fc_id", "inventory_id", "quantidade", "dt_pedido", "dt_limite_expedicao",
                                         "dt_inicio_picking", "dt_fim_packing", "dt_expedicao", "status"])
pedidos = pedidos[pedidos["dt_pedido"] <= FIM + pd.Timedelta(hours=23, minutes=59)]
pend = pedidos["status"].eq("EXPEDIDO") & pedidos["dt_inicio_picking"].isna()
pedidos.loc[pend, "status"] = "PENDENTE"

exp = pedidos[pedidos["status"] == "EXPEDIDO"]
p_err = exp["fc_id"].map(p_erro_fc) * np.where(exp["dt_inicio_picking"].dt.hour >= 14, 1.35, 1.0)
mask = rng.random(len(exp)) < p_err
oc = exp[mask]
ocorrencias = pd.DataFrame({
    "ocorrencia_id": [f"OC{900000 + i}" for i in range(mask.sum())],
    "order_id": oc["order_id"].values,
    "tipo": rng.choice(["ITEM_ERRADO", "ITEM_FALTANTE", "QUANTIDADE_DIVERGENTE", "AVARIA_NA_EMBALAGEM"], mask.sum(), p=[0.42, 0.25, 0.2, 0.13]),
    "data_registro": (oc["dt_expedicao"] + pd.to_timedelta(rng.uniform(1, 6, mask.sum()), unit="D")).dt.date.values,
})

rec, n_asn = [], 0
for f, fc in enumerate(FC):
    idx_fc = np.nonzero(fc_sku == f)[0]
    w = pop[idx_fc] / pop[idx_fc].sum()
    for d, dt in enumerate(dias):
        if dt.dayofweek == 6:
            continue
        alvo = saida_dia_fc[max(0, d - 3):d + 1, f].mean() * 1.18 * rng.uniform(0.8, 1.25)
        tot = 0
        while tot < alvo:
            n_asn += 1
            s0 = rng.choice(idx_fc, p=w)
            do_seller = idx_fc[seller_idx[idx_fc] == seller_idx[s0]]
            linhas = rng.choice(do_seller, min(len(do_seller), rng.integers(1, 7)), replace=False)
            ag = dt + pd.Timedelta(hours=int(rng.integers(7, 17)))
            chegada = ag + pd.Timedelta(minutes=float(rng.normal(4, 16) if rng.random() > 0.08 else rng.uniform(60, 300)))
            atraso_conf = rng.gamma(2, 1.1) * (1.7 if fc == "BA01" else 1.0)
            fim_conf = chegada + pd.Timedelta(hours=float(0.4 + atraso_conf))
            fim_arm = fim_conf + pd.Timedelta(hours=float(rng.gamma(1.6, 5) * (1.5 if fc == "BA01" else 1.0)))
            for s in linhas:
                dec = int(np.clip(round(pop[s] * rng.uniform(8, 25)), 5, 240))
                r = rng.random()
                recq = dec if r > 0.045 else max(0, dec + int(rng.choice([-1, 1]) * rng.integers(1, max(2, dec // 8))))
                av = int(rng.binomial(recq, 0.003 * cats[cat_sku[s]]["risco"]))
                rec.append((f"ASN{700000 + n_asn}", skus["seller_id"].iat[s], fc, skus["inventory_id"].iat[s], ag, chegada, fim_conf, fim_arm, dec, recq, av))
                tot += recq
recebimentos = pd.DataFrame(rec, columns=["asn_id", "seller_id", "fc_id", "inventory_id", "dt_agendamento", "dt_chegada",
                                          "dt_fim_conferencia", "dt_fim_armazenagem", "qtd_declarada", "qtd_recebida", "qtd_avariada"])

for proc, col, uphd in [("RECEBIMENTO", "dt_fim_conferencia", uph_rec), ("ARMAZENAGEM", "dt_fim_armazenagem", uph_arm)]:
    t = recebimentos[col]
    tmp = pd.DataFrame({"data": t.dt.date, "fc": recebimentos["fc_id"],
                        "turno": np.where((t.dt.hour >= 6) & (t.dt.hour < 14), "T1", np.where((t.dt.hour >= 14) & (t.dt.hour < 22), "T2", "T3")),
                        "u": recebimentos["qtd_recebida"]})
    g = tmp.groupby(["data", "fc", "turno"], as_index=False)["u"].sum()
    for _, r in g.iterrows():
        if pd.Timestamp(r["data"]) > FIM:
            continue
        u_ref = uphd[r["fc"]] * rng.uniform(0.9, 1.08)
        horas = max(1.0, r["u"] / u_ref * rng.uniform(1.0, 1.12))
        apont.append((r["data"], r["fc"], r["turno"], proc, int(np.ceil(horas / 7.33)), round(horas, 2), int(r["u"])))
apontamentos = pd.DataFrame(apont, columns=["data", "fc_id", "turno", "processo", "colaboradores", "horas_trabalhadas", "unidades"])
apontamentos = apontamentos.sort_values(["data", "fc_id", "turno", "processo"]).reset_index(drop=True)

venda_dia = pedidos[pedidos["dt_pedido"] >= FIM - pd.Timedelta(days=60)].groupby("inventory_id")["quantidade"].sum() / 61
vd = venda_dia.reindex(skus["inventory_id"]).fillna(0).values
cobertura_alvo = rng.lognormal(np.log(30), 0.6, N_SKU)
cobertura_alvo[lento] = rng.uniform(150, 400, lento.sum())
estoque = np.maximum(np.round(np.maximum(vd, 0.08) * cobertura_alvo), rng.integers(1, 6, N_SKU)).astype(int)
estoque[rng.random(N_SKU) < 0.03] = 0

ruas = {"SP01": 40, "MG01": 26, "BA01": 18}
pos_rows, enderecos_fc = [], {fc: [] for fc in FC}
usados = set()
for s in range(N_SKU):
    fc = FC[fc_sku[s]]
    if estoque[s] == 0:
        continue
    n_end = 1 if estoque[s] < 40 else (2 if estoque[s] < 200 else 3)
    partes = np.maximum(1, np.round(rng.dirichlet(np.ones(n_end)) * estoque[s])).astype(int)
    partes[-1] = max(1, estoque[s] - partes[:-1].sum())
    for q in partes:
        while True:
            e = f"{fc}-{chr(65 + rng.integers(0, 6))}{rng.integers(1, ruas[fc]):02d}-{rng.integers(1, 41):02d}-{rng.integers(1, 6)}"
            if e not in usados:
                usados.add(e)
                break
        enderecos_fc[fc].append((e, s))
        n_lotes = rng.integers(1, 4)
        lq = np.maximum(1, np.round(rng.dirichlet(np.ones(n_lotes)) * q)).astype(int)
        lq[-1] = max(1, q - lq[:-1].sum())
        for l in lq:
            idade = int(min(700, rng.exponential(cobertura_alvo[s] * 0.8) + rng.integers(0, 10)))
            pos_rows.append((fc, e, skus["inventory_id"].iat[s], (FIM - pd.Timedelta(days=idade)).date(), int(l)))
posicao = pd.DataFrame(pos_rows, columns=["fc_id", "endereco", "inventory_id", "data_entrada_lote", "quantidade"])
ocup = posicao.groupby("fc_id")["endereco"].nunique()
fcs["capacidade_posicoes"] = [int(round(ocup[fc] / u, -1)) for fc, u in zip(FC, [0.91, 0.84, 0.73])]

cont, n_c = [], 0
cnt_dia = {"SP01": 70, "MG01": 38, "BA01": 26}
for d, dt in enumerate(dias):
    for fc in FC:
        lista = enderecos_fc[fc]
        for k in rng.choice(len(lista), cnt_dia[fc], replace=False):
            e, s = lista[k]
            n_c += 1
            sist = int(max(0, round(estoque[s] * rng.uniform(0.2, 0.8))))
            p = p_div_fc[fc] * cats[cat_sku[s]]["risco"]
            if rng.random() < p:
                delta = int(rng.choice([-3, -2, -1, -1, -1, -1, 1, 1, 2]))
                c1 = max(0, sist + delta)
            else:
                c1 = sist
            if c1 != sist:
                rec_q = sist if rng.random() < 0.35 else c1
            else:
                rec_q = None
            final = sist if rec_q is None else rec_q
            cont.append((f"CC{500000 + n_c}", dt.date(), fc, e, skus["inventory_id"].iat[s], sist, c1, rec_q, final,
                         f"OP{rng.integers(100, 160) if fc == 'SP01' else rng.integers(200, 230) if fc == 'MG01' else rng.integers(300, 318)}"))
contagens = pd.DataFrame(cont, columns=["contagem_id", "data", "fc_id", "endereco", "inventory_id", "qtd_sistema",
                                        "qtd_contagem_1", "qtd_recontagem", "qtd_final", "operador"])

aj = contagens[contagens["qtd_final"] != contagens["qtd_sistema"]]
ajustes = pd.DataFrame({"data": aj["data"], "fc_id": aj["fc_id"], "inventory_id": aj["inventory_id"],
                        "qtd_ajuste": aj["qtd_final"] - aj["qtd_sistema"], "motivo": "CONTAGEM_CICLICA", "referencia": aj["contagem_id"]})
n_av = 520
av_idx = rng.choice(N_SKU, n_av, p=pop / pop.sum())
ajustes = pd.concat([ajustes, pd.DataFrame({
    "data": [dias[k].date() for k in rng.integers(0, ND, n_av)], "fc_id": np.array(FC)[fc_sku[av_idx]],
    "inventory_id": skus["inventory_id"].values[av_idx], "qtd_ajuste": -rng.integers(1, 3, n_av),
    "motivo": rng.choice(["AVARIA_INTERNA", "EXTRAVIO", "VENCIMENTO"], n_av, p=[0.7, 0.22, 0.08]), "referencia": None})])
ajustes = ajustes.sort_values("data").reset_index(drop=True)
ajustes.insert(0, "ajuste_id", [f"AJ{300000 + i}" for i in range(len(ajustes))])

# ---------- sujeira de extração ----------
p = pedidos.copy()
n = len(p)
for c in ["dt_pedido", "dt_limite_expedicao", "dt_inicio_picking", "dt_fim_packing", "dt_expedicao"]:
    s = p[c].dt.strftime("%Y-%m-%d %H:%M:%S")
    br = rng.random(n) < 0.1
    s[br] = p.loc[br, c].dt.strftime("%d/%m/%Y %H:%M")
    p[c] = s.where(p[c].notna(), "")
var_st = {"EXPEDIDO": ["expedido", "Expedido ", "EXPEDIDO "], "CANCELADO_FALTA_ESTOQUE": ["CANCELADO - FALTA ESTOQUE", "cancelado_falta_estoque"],
          "CANCELADO_CLIENTE": ["Cancelado Cliente"], "PENDENTE": ["pendente"]}
i = rng.random(n) < 0.06
p.loc[i, "status"] = [rng.choice(var_st[s]) for s in p.loc[i, "status"]]
i = rng.random(n) < 0.04
p.loc[i, "fc_id"] = [rng.choice([f"fc-{x.lower()}", f"FC-{x}", f" {x}"]) for x in p.loc[i, "fc_id"]]
i = rng.random(n) < 0.02
p.loc[i, "inventory_id"] = p.loc[i, "inventory_id"].str.lower()
p = pd.concat([p, p.sample(frac=0.005, random_state=SEED)]).sample(frac=1, random_state=SEED).reset_index(drop=True)

r = recebimentos.copy()
for c in ["dt_agendamento", "dt_chegada", "dt_fim_conferencia", "dt_fim_armazenagem"]:
    r[c] = r[c].dt.strftime("%Y-%m-%d %H:%M:%S")
r["qtd_recebida"] = r["qtd_recebida"].astype(str)
i = rng.random(len(r)) < 0.05
r.loc[i, "qtd_recebida"] = r.loc[i, "qtd_recebida"] + ",0"
r = pd.concat([r, r.sample(frac=0.004, random_state=SEED)]).reset_index(drop=True)

s = skus.copy()
s["preco_venda"] = [f"{v:.2f}".replace(".", ",") if rng.random() < 0.25 else f"{v:.2f}" for v in s["preco_venda"]]
i = rng.random(len(s)) < 0.1
s.loc[i, "categoria"] = [rng.choice([c.upper(), c.lower(), f" {c}"]) for c in s.loc[i, "categoria"]]

ct = contagens.copy()
ct["qtd_recontagem"] = ct["qtd_recontagem"].astype("Int64").astype(str).replace("<NA>", "")
i = rng.random(len(ct)) < 0.01
ct.loc[i, "operador"] = ""

fcs.to_csv(OUT / "fcs.csv", index=False)
sellers.to_csv(OUT / "sellers.csv", index=False)
s.drop(columns="fc_id").assign(fc_id=skus["fc_id"]).to_csv(OUT / "skus.csv", index=False, sep=";")
p.to_csv(OUT / "pedidos.csv.gz", index=False, compression="gzip")
ocorrencias.to_csv(OUT / "ocorrencias_qualidade.csv", index=False)
r.to_csv(OUT / "recebimentos.csv", index=False, sep=";")
apontamentos.to_csv(OUT / "apontamentos_produtividade.csv", index=False)
ct.to_csv(OUT / "contagens_ciclicas.csv", index=False)
ajustes.to_csv(OUT / "ajustes_inventario.csv", index=False)
posicao.to_csv(OUT / "posicao_estoque.csv", index=False)

for f in sorted(OUT.iterdir()):
    df = pd.read_csv(f, sep=None, engine="python") if f.suffix != ".gz" else pd.read_csv(f)
    print(f"{f.name:32s} {len(df):>9,} linhas  {f.stat().st_size/1e6:6.1f} MB")
