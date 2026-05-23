# Medical Comparison: Cortisol vs. Cortisone

## Overview
Cortisol and Cortisone are closely related corticosteroids, but they differ in biological activity and potency.

## Biological Activity
- **Cortisol (Hydrocortisone)**: The biologically active form of the hormone. It can directly bind to glucocorticoid receptors to exert its effects.
- **Cortisone**: A prodrug (biologically inactive). It must be converted into Cortisol to become active.

## Activation Pathway
The conversion of Cortisone to Cortisol is mediated by the enzyme **11β-hydroxysteroid dehydrogenase type 1 (11β-HSD1)**, which is primarily located in the liver but also found in other tissues like adipose tissue and the brain. Conversely, Cortisol is converted back to Cortisone by **11β-HSD2**, primarily in the kidneys.

![Chemical Balance: Cortisone <=> Cortisol](output/images/chemical_balance.png)

![11β-HSD1 Enzyme (PDB 1XU7) with highlighted Active Center (NDP and Catalytic Residues)](output/images/enzyme_11bhsd1.png)

## Pharmacological Significance and Clinical Relevance
The clinical relevance of these molecules is defined by their biological activity and therapeutic efficacy.
- **Cortisol (Hydrocortisone)**: As the active hormone, it represents the primary mediator of glucocorticoid effects. Its pharmacological significance lies in its immediate availability for receptor binding, making it essential for acute replacement therapy and emergency situations (e.g., Addisonian crisis).
- **Cortisone**: Its quality as a medication is characterized by its role as a prodrug. It requires metabolic activation, which provides a slower onset of action compared to direct cortisol administration. This makes it suitable for chronic conditions where a steadier, less acute effect is desired.

## Relative Potency
- **Cortisol**: Relative Potency = 1 (Reference standard).
- **Cortisone**: Relative Potency ≈ 0.8. Cortisone is generally considered slightly less potent than Cortisol due to the requirement for enzymatic activation.

## Signaling Chain
The signaling pathway of Cortisol (and activated Cortisone) involves several distinct stages:
1. **Cellular Entry**: Being lipophilic, Cortisol diffuses freely across the cell membrane into the cytoplasm.
2. **Receptor Binding**: In the cytoplasm, Cortisol binds to the **[Glucocorticoid Receptor (NR3C1 / GR)](https://www.proteinatlas.org/ENSG00000113580-NR3C1)**, which is typically held in an inactive state by a chaperone complex including **[HSP90 (HSP90AA1)](https://www.proteinatlas.org/ENSG00000080824-HSP90AA1)**, **[HSP70 (HSPA1A)](https://www.proteinatlas.org/ENSG00000204389-HSPA1A)**, and **[FKBP5](https://www.proteinatlas.org/ENSG00000096060-FKBP5)** (which reduces binding affinity).
3. **Activation**: Binding triggers the dissociation of these chaperone proteins. During this process, FKBP5 is often replaced by **[FKBP4](https://www.proteinatlas.org/ENSG00000004478-FKBP4)**, which supports the conformational change and increases binding affinity.
4. **Nuclear Translocation**: The activated Cortisol-GR complex translocates into the nucleus, with FKBP4 mediating the interaction with the **[dynein transport protein (DYNC1H1)](https://www.proteinatlas.org/ENSG00000197102-DYNC1H1)**.
5. **Biological Response**:
    - **Transactivation**: The complex binds to specific DNA sequences called **Glucocorticoid Response Elements (GREs)**, stimulating the transcription of anti-inflammatory and metabolic genes.
    - **Transrepression**: The complex can also interfere with the activity of other transcription factors, such as **[NF-κB (NFKB1)](https://www.proteinatlas.org/ENSG00000109320-NFKB1)** or **[AP-1 (JUN)](https://www.proteinatlas.org/ENSG00000177606-JUN)**, thereby repressing the expression of pro-inflammatory genes.

## Therapeutic Use Cases
### Cortisol (Hydrocortisone)
- **Adrenal Insufficiency**: Primary treatment for Addison's disease.
- **Acute Allergic Reactions**: Used for rapid effect in severe allergies.
- **Topical Applications**: Common in creams for skin inflammation and itching.

### Cortisone
- **Joint and Tendon Inflammation**: Historically known as "cortisone shots," though today synthetic derivatives like triamcinolone or direct-acting hydrocortisone are mostly used, as cortisone would first need to be activated locally.
- **Systemic Inflammation**: Used orally for various autoimmune and inflammatory conditions where a prodrug approach is acceptable.

## Key Differences
| Feature | Cortisol (Hydrocortisone) | Cortisone |
|---------|---------------------------|-----------|
| **Form** | Active Hormone | Inactive Prodrug |
| **Primary Site of Action** | Systemic / Tissues | Must be activated in Liver/Tissues |
| **Half-life** | Plasma: ~1.5 - 2 h; Biological: 8 - 12 h | Plasma: ~0.5 - 1 h (rapid activation) |
| **Mineralocorticoid Activity** | High (potential), but enzymatically protected | None (inactive at receptor) |
