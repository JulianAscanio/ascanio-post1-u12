# Análisis del Impacto Cuántico en Ciberseguridad y Estrategia de Migración Post-Cuántica (PQC)

**Asignatura:** Arquitectura de Computadores  
**Unidad 12:** Post-contenido (Parte 2)  
**Estudiante:** Julian Andres Ascanio  
**Repositorio:** `ascanio-post1-u12`

---

## 1. Inventario de Algoritmos Criptográficos Vulnerables

La llegada de computadoras cuánticas tolerantes a fallos (*Cryptographically Relevant Quantum Computers*, CRQC) plantea una amenaza asimétrica sobre los mecanismos criptográficos vigentes. Mientras que los algoritmos de clave pública basados en la factorización de enteros o el logaritmo discreto resultan **rotos completamente** mediante el algoritmo de Shor en tiempo polinomial, los algoritmos simétricos y las funciones *hash* sufren únicamente un **debilitamiento cuadrático** mediante el algoritmo de Grover, el cual puede mitigarse duplicando la longitud de las claves o de los resúmenes criptográficos (National Institute of Standards and Technology [NIST], 2024a; CISA, NSA y NIST, 2023).

La distinción entre ambos niveles de impacto es crítica para la gestión del riesgo: un algoritmo clasificado como *roto completamente* compromete de forma retroactiva la confidencialidad de datos interceptados en el presente y almacenados para su descifrado futuro (*Harvest Now, Decrypt Later*, HNDL), mientras que un algoritmo *debilitado* conserva un margen de seguridad utilizable si se ajustan sus parámetros.

| Algoritmo | Tipo | Vulnerabilidad cuántica | Algoritmo atacante | Estado post-cuántico |
| :--- | :--- | :--- | :--- | :--- |
| **RSA-2048 / 4096** | Cifrado asimétrico / Firma | **Roto completamente** (compromete confidencialidad retroactiva) | Shor $\mathcal{O}(n^3)$ | Reemplazar con **ML-KEM** (cifrado/KEM) o **ML-DSA / SLH-DSA** (firma) |
| **ECDSA (P-256, P-384)** | Firma digital | **Roto completamente** (falsificación de firmas y compromiso de autenticación) | Shor (logaritmo discreto en curva elíptica) | Reemplazar con **ML-DSA** o **SLH-DSA** |
| **ECDH / X25519** | Intercambio de clave (KEX) | **Roto completamente** (expuesto a ataques HNDL sobre tráfico capturado) | Shor (logaritmo discreto en curva elíptica) | Reemplazar con **ML-KEM** (en transición híbrida con X25519) |
| **AES-128** | Cifrado simétrico | **Debilitado** (seguridad efectiva reducida a ~64 bits) | Grover $\mathcal{O}(\sqrt{N})$ | Migrar a **AES-256** |
| **AES-256** | Cifrado simétrico | **Aceptable** (seguridad efectiva ~128 bits post-cuánticos) | Grover $\mathcal{O}(\sqrt{N})$ | Mantener con precaución como estándar simétrico |
| **SHA-256** | Función *hash* | **Debilitado** (búsqueda de preimagen a $2^{128}$ y colisiones afectadas) | Grover | Migrar a **SHA-384** o **SHA-512** para resistencia a largo plazo |
| **SHA-3-256** | Función *hash* | **Debilitado** (equivalente a SHA-256 en tamaño de digest) | Grover | Usar **SHA-3-384** o **SHA-3-512** |

---

## 2. Estándares NIST PQC 2024 — Análisis Comparativo

En agosto de 2024, el NIST publicó los tres primeros estándares federales de criptografía post-cuántica (PQC): **FIPS 203**, **FIPS 204** y **FIPS 205**. Estos estándares establecen el reemplazo directo de la criptografía asimétrica clásica: **ML-KEM** sustituye a ECDH y RSA en el establecimiento de claves compartidas, mientras que **ML-DSA** y **SLH-DSA** sustituyen a ECDSA y RSA en la generación y verificación de firmas digitales (NIST, 2024a, 2024b, 2024c).

### 2.1 ML-KEM (FIPS 203 — CRYSTALS-Kyber)

**ML-KEM** (*Module-Lattice-Based Key-Encapsulation Mechanism*) es un mecanismo de encapsulamiento de claves fundamentado en la dificultad del problema *Module Learning with Errors* (MLWE) sobre retículos algebraicos (NIST, 2024a). Se define en tres conjuntos de parámetros que corresponden a las categorías de seguridad 1, 3 y 5 del NIST (equivalentes a AES-128, AES-192 y AES-256 frente a búsqueda exhaustiva):

- **ML-KEM-512 (Categoría 1):** Clave pública de 800 bytes, clave privada de 1632 bytes y *ciphertext* de 768 bytes.
- **ML-KEM-768 (Categoría 3):** Clave pública de 1184 bytes, clave privada de 2400 bytes y *ciphertext* de 1088 bytes. Es el perfil recomendado por defecto para uso general en Internet y protocolos TLS.
- **ML-KEM-1024 (Categoría 5):** Clave pública de 1568 bytes, clave privada de 3168 bytes y *ciphertext* de 1568 bytes.

### 2.2 ML-DSA (FIPS 204 — CRYSTALS-Dilithium)

**ML-DSA** (*Module-Lattice-Based Digital Signature Algorithm*) es un esquema de firma digital basado igualmente en los problemas MLWE y *Module Short Integer Solution* (MSIS) (NIST, 2024b). Sus tres variantes ofrecen un equilibrio entre tamaño de firma y nivel de seguridad:

- **ML-DSA-44 (Categoría 2):** Clave pública de 1312 bytes, clave privada de 2560 bytes y firma de 2420 bytes.
- **ML-DSA-65 (Categoría 3):** Clave pública de 1952 bytes, clave privada de 4032 bytes y firma de 3309 bytes.
- **ML-DSA-87 (Categoría 5):** Clave pública de 2592 bytes, clave privada de 4896 bytes y firma de 4627 bytes.

Frente a **ECDSA P-256** (clave pública de 64 bytes y firma DER de ~70–72 bytes), ML-DSA-65 produce firmas aproximadamente 46 veces más grandes; sin embargo, sus operaciones basadas en multiplicación de polinomios mediante *Number Theoretic Transform* (NTT) ofrecen velocidades de firma y verificación altamente competitivas en arquitecturas modernas (NIST, 2024b).

### 2.3 SLH-DSA (FIPS 205 — SPHINCS+)

**SLH-DSA** (*Stateless Hash-Based Digital Signature Algorithm*) es un esquema de firma digital sin estado basado únicamente en la seguridad de funciones *hash* criptográficas (SHA-2 o SHAKE), sin depender de suposiciones algebraicas sobre retículos (NIST, 2024c). Esta propiedad hace de SLH-DSA una alternativa más conservadora frente a posibles avances futuros en criptoanálisis de retículos. Como contrapartida, sus firmas son considerablemente más extensas (desde 7856 bytes en **SLH-DSA-128s** hasta 49 856 bytes en variantes de categoría 5) y su generación de firma es significativamente más lenta que la de ML-DSA, por lo que se recomienda principalmente como mecanismo de respaldo, diversidad criptográfica o para autoridades de certificación raíz con baja frecuencia de firma.

### 2.4 Tabla Comparativa de Estándares NIST PQC

| Estándar y variante | Problema matemático | Clave pública (B) | Clave privada (B) | Firma / Ciphertext (B) | Velocidad relativa | Reemplazo de | Fuente |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- | :--- |
| **ML-KEM-512** | MLWE (retículos) | 800 | 1632 | 768 (ct) | Muy alta (sub-ms) | ECDH / RSA-KEM | NIST FIPS 203 (2024a) |
| **ML-KEM-768** | MLWE (retículos) | 1184 | 2400 | 1088 (ct) | Muy alta (sub-ms) | ECDH / X25519 | NIST FIPS 203 (2024a) |
| **ML-KEM-1024** | MLWE (retículos) | 1568 | 3168 | 1568 (ct) | Alta | ECDH P-384 / RSA | NIST FIPS 203 (2024a) |
| **ML-DSA-44** | MLWE / MSIS | 1312 | 2560 | 2420 (firma) | Alta | ECDSA P-256 | NIST FIPS 204 (2024b) |
| **ML-DSA-65** | MLWE / MSIS | 1952 | 4032 | 3309 (firma) | Alta | ECDSA P-256 / P-384 | NIST FIPS 204 (2024b) |
| **ML-DSA-87** | MLWE / MSIS | 2592 | 4896 | 4627 (firma) | Media-alta | ECDSA P-384 / RSA | NIST FIPS 204 (2024b) |
| **SLH-DSA-128s** | Funciones *hash* | 32 | 64 | 7856 (firma) | Baja en firma / Media en verificación | ECDSA (respaldo) | NIST FIPS 205 (2024c) |

---

## 3. Plan de Migración para Tres Perfiles Organizacionales

Siguiendo las guías de transición de CISA, NSA y NIST (2023) y de ETSI GR QSC 006 (2024), el plan de migración prioriza los activos según el horizonte de sensibilidad de la información y la exposición al ataque HNDL.

### 3.1 Perfil A — Hospital Universitario

- **Inventario de sistemas con criptografía asimétrica:** Portal de pacientes y APIs clínicas sobre TLS 1.3 (actualmente ECDHE/X25519 + ECDSA), sistemas de historia clínica electrónica (EHR), túneles VPN entre sedes hospitalarias y plataforma de firma digital de prescripciones médicas (ECDSA).
- **Clasificación por horizonte de sensibilidad:** Datos clínicos e historial genómico/médico con sensibilidad crítica de **50 a 75 años**. La amenaza HNDL es máxima, dado que tráfico capturado hoy conservará valor sensible cuando existan computadoras cuánticas operativas.
- **Estrategia híbrida de transición:** Despliegue inmediato de intercambio de claves híbrido `X25519MLKEM768` en terminación TLS del portal y VPNs, manteniendo autenticación clásica ECDSA en paralelo con pruebas piloto de certificados ML-DSA-65 en entornos internos hasta que los clientes/navegadores completen el soporte de PKI PQC.
- **Cronograma de migración:**
  - *Hito 1 (Meses 1–4):* Descubrimiento automatizado de inventario criptográfico (CBOM) y habilitación de TLS híbrido `X25519MLKEM768` en balanceadores y VPNs perimetrales.
  - *Hito 2 (Meses 5–12):* Migración del servicio de firma de prescripciones médicas hacia ML-DSA-65 con validación en portal clínico y actualización de módulos HSM.
  - *Hito 3 (Meses 13–24):* Renovación de la PKI interna hospitalaria hacia cadenas híbridas/PQC y auditoría de cumplimiento sobre repositorios EHR.
- **Riesgos y mitigaciones:** Incompatibilidad con equipos médicos heredados (*legacy*); se mitiga mediante segmentación de red y pasarelas TLS híbridas (*reverse proxies*) frente a dispositivos sin soporte nativo.

### 3.2 Perfil B — Startup de Comercio Electrónico

- **Inventario de sistemas con criptografía asimétrica:** Infraestructura web y pasarela de pagos con TLS 1.3 (`X25519` + `ECDSA`), cifrado simétrico `AES-256-GCM`, firma de *tokens* JWT/API y cumplimiento PCI-DSS.
- **Clasificación por horizonte de sensibilidad:** Datos de tarjetas y transacciones con vida útil operativa de **5 a 7 años**. La exposición a HNDL a largo plazo es moderada-baja, pero la adopción temprana de TLS PQC híbrido aporta diferenciación comercial y compatibilidad con navegadores modernos.
- **Estrategia híbrida de transición:** Activación de `X25519MLKEM768` en CDN y servidores *edge* TLS 1.3 para proteger el intercambio de claves sin romper compatibilidad con clientes móviles antiguos (negociación *fallback* a X25519).
- **Cronograma de migración:**
  - *Hito 1 (Meses 1–3):* Habilitación de intercambio de claves híbrido en CDN/proxy inverso y verificación de latencia en *checkout*.
  - *Hito 2 (Meses 4–9):* Actualización de librerías criptográficas internas (OpenSSL 3.5+ / BoringSSL) para firma de *tokens* internos con agilidad criptográfica (*crypto-agility*).
  - *Hito 3 (Meses 10–18):* Evaluación de certificados ML-DSA conforme las autoridades de certificación públicas (CA/Browser Forum) habiliten emisión estándar.
- **Riesgos y mitigaciones:** Posible incremento de fragmentación TCP en clientes móviles con redes de alta pérdida; se mitiga midiendo métricas de latencia real (*RUM*) y manteniendo `X25519MLKEM768` únicamente en intercambio de claves mientras los certificados permanecen en ECDSA en el corto plazo.

### 3.3 Perfil C — Entidad Gubernamental de Defensa

- **Inventario de sistemas con criptografía asimétrica:** Comunicaciones clasificadas, infraestructura nacional de clave pública (PKI), VPNs IPsec/IKEv2 inter-agencias, correo seguro (S/MIME) y firma de documentos oficiales y actualizaciones de *firmware*.
- **Clasificación por horizonte de sensibilidad:** Información clasificada y estratégica con sensibilidad de **25 a 50 años**. La migración es obligatoria conforme a los plazos de **CNSA 2.0** (NSA, 2022) entre **2025 y 2033**.
- **Estrategia híbrida de transición:** Uso transitorio de esquemas híbridos clasificados aprobados únicamente durante la coexistencia con socios inter-agencias, ejecutando una transición estructurada hacia algoritmos puros CNSA 2.0 (ML-KEM-1024, ML-DSA-87 y LMS/XMSS o SLH-DSA para firma de *firmware* y raíces).
- **Cronograma de migración:**
  - *Hito 1 (2025–2026):* Criptografía de agilidad obligatoria en nuevas adquisiciones y migración de firma de *software/firmware* a esquemas basados en *hash* aprobados.
  - *Hito 2 (2027–2030):* Transición de VPNs inter-agencias, TLS gubernamental y navegadores internos a ML-KEM-1024 y ML-DSA-87 (alineado con transición CNSA 2.0 por defecto en 2030).
  - *Hito 3 (2031–2033):* Retiro total de algoritmos clásicos vulnerables a Shor en sistemas de seguridad nacional antes del límite de 2033.
- **Riesgos y mitigaciones:** Bloqueo de cadena de suministro en hardware HSM/criptográfico certificado FIPS 140-3; se mitiga exigiendo hoja de ruta PQC contractual a proveedores desde las licitaciones de 2025.

---

## 4. Comparación de Tamaños de Clave/Firma: PQC vs. Criptografía Clásica y su Impacto en TLS 1.3 Híbrido

La adopción de estándares post-cuánticos conlleva un incremento sustancial en el tamaño en bytes de claves públicas, *ciphertexts* y firmas respecto a la criptografía de curvas elípticas (ECC) y RSA (NIST, 2024a, 2024b, 2024c).

| Algoritmo | Tipo | Clave pública | Clave privada | Firma / Ciphertext | Nivel de seguridad NIST | Fuente |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| **RSA-3072** | Cifrado/firma clásico | ~400 bytes | ~1600 bytes | 384 bytes (firma) | ~128 bits clásicos (no post-cuántico) | NIST SP 800-57 |
| **ECDSA P-256** | Firma clásica | 64 bytes | 32 bytes | ~70–72 bytes (DER) | ~128 bits clásicos (no post-cuántico) | FIPS 186-5 |
| **X25519** | Intercambio de clave clásico | 32 bytes | 32 bytes | N/A (KEX, no firma) | ~128 bits clásicos (no post-cuántico) | RFC 7748 |
| **ML-KEM-768** | KEM post-cuántico | 1184 bytes | 2400 bytes | 1088 bytes (*ciphertext*) | Nivel NIST 3 (≈ AES-192) | NIST FIPS 203 (2024a) |
| **ML-DSA-65** | Firma post-cuántica | 1952 bytes | 4032 bytes | 3309 bytes (firma) | Nivel NIST 3 (≈ AES-192) | NIST FIPS 204 (2024b) |
| **SLH-DSA-128s** | Firma post-cuántica (*hash*) | 32 bytes | 64 bytes | 7856 bytes (firma) | Nivel NIST 1 (≈ AES-128) | NIST FIPS 205 (2024c) |

### Impacto cuantitativo en un Handshake TLS 1.3 Híbrido

La diferencia de escala es significativa: la clave pública de **ML-KEM-768** es **37 veces mayor** que la de X25519 (1184 frente a 32 bytes), y una firma de **ML-DSA-65** es aproximadamente **46 veces mayor** que una firma ECDSA P-256 (3309 frente a ~72 bytes).

En un *handshake* TLS 1.3 con intercambio de clave híbrido `X25519+ML-KEM-768` —desplegado en producción por Chrome y Cloudflare inicialmente como `X25519Kyber768` y estandarizado posteriormente como `X25519MLKEM768` (Kwiatkowski et al., 2024)—:
- El campo `key_share` del mensaje `ClientHello` pasa de **32 bytes** (X25519 solo) a aproximadamente **1216 bytes** ($32 + 1184$ bytes).
- La respuesta `key_share` del `ServerHello` pasa de **32 bytes** a aproximadamente **1120 bytes** ($32 + 1088$ bytes).

En redes con conectividad estable, un `ClientHello` de ~1.3–1.5 KB sigue cabiendo dentro de la ventana inicial de congestión de TCP (*Initial Congestion Window*, típicamente `IW10`, equivalente a ~14 KB en Ethernet con MSS de 1460 bytes), por lo que en el caso común **no introduce rondas de red adicionales (RTT)** (Westerbaan y Sullivan, 2023). Sin embargo, si el intercambio híbrido se combina con una cadena de certificados firmada íntegramente con **ML-DSA-65** (donde cada firma aporta ~3.3 KB y cada clave pública ~1.95 KB), el bloque `Certificate` + `CertificateVerify` crece en más de 10–15 KB respecto a una cadena ECDSA equivalente. Bajo ese escenario, el volumen total del *handshake* supera la ventana inicial de TCP, se fragmenta en múltiples paquetes y, en enlaces con alta latencia, pérdida de paquetes o *middleboxes* restrictivos, provoca retransmisiones y rondas adicionales que incrementan la latencia percibida.

---

## 5. Decisiones Técnicas — Parte 2

### Decisión Técnica 3: ¿Qué algoritmo NIST es el correcto para firmar las prescripciones digitales del Perfil A?

Para firmar digitalmente las prescripciones médicas del Perfil A (hospital universitario), **ML-KEM (FIPS 203)** queda descartado de entrada porque es un mecanismo de encapsulamiento de claves (KEM) destinado al establecimiento de secretos compartidos, no un esquema de firma digital. La elección se restringe por tanto a los dos estándares de firma: **ML-DSA-65 (FIPS 204)** y **SLH-DSA-128s (FIPS 205)**.

Según los datos de la Sección 4, un hospital universitario que emite miles de prescripciones diarias con requisitos de baja latencia en su portal clínico se ve favorecido de forma determinante por **ML-DSA-65**: su firma ocupa **3309 bytes** frente a los **7856 bytes** de **SLH-DSA-128s** (menos de la mitad de tamaño en almacenamiento, ancho de banda y carga de PDF/JSON firmados) y, al basarse en retículos (MLWE/MSIS) mediante operaciones NTT, ofrece tiempos de generación y verificación muy superiores a los esquemas basados únicamente en *hash*. Aunque SLH-DSA posee una asunción de seguridad más conservadora —al depender exclusivamente de la resistencia a colisiones y preimagen de funciones *hash*—, es fundamental distinguir entre confidencialidad y autenticidad: la amenaza HNDL compromete el *cifrado* de historias clínicas cuya confidencialidad debe durar 50–75 años, pero una firma de prescripción busca autenticar la autoría e integridad en el momento de emisión y dispensación. Por ello, **se selecciona ML-DSA-65 como algoritmo principal** para las prescripciones del Perfil A, reservando **SLH-DSA** como alternativa de respaldo y diversidad criptográfica para certificados raíz de larga vida o firma de *firmware* crítico.

### Decisión Técnica 4: ¿Modo híbrido permanente o etapa de transición para el Perfil B?

Para el Perfil B (startup de comercio electrónico con horizonte de sensibilidad de 5–7 años), la adopción inmediata del **modo híbrido clásico+PQC (`X25519+ML-KEM-768`)** en TLS 1.3 es la decisión técnica más acertada como **etapa de transición**, mas no como arquitectura permanente. Como se cuantificó en la Sección 4, el incremento del `key_share` a ~1216 bytes en el `ClientHello` y ~1120 bytes en el `ServerHello` rara vez añade rondas de red adicionales en condiciones normales de conectividad, por lo que el costo en latencia percibida para la experiencia de compra es prácticamente nulo, tal como han demostrado los despliegues masivos en navegadores y CDNs modernas (Westerbaan y Sullivan, 2023).

A cambio de ese sobrecosto marginal, el modo híbrido otorga una doble protección frente a dos riesgos independientes y no correlacionados: (1) una eventual ruptura cuántica de la criptografía clásica (`X25519` / ECC), y (2) el descubrimiento de una vulnerabilidad clásica inesperada en los algoritmos PQC recién estandarizados (`ML-KEM`), los cuales cuentan con muchos menos años de escrutinio criptoanalítico público que ECC. Esta cobertura dual resulta especialmente valiosa durante la ventana actual de maduración del ecosistema. No obstante, dado que el modo híbrido introduce mayor complejidad de implementación y un consumo adicional real de ancho de banda y cómputo, no debe mantenerse indefinidamente: una vez que ML-KEM y ML-DSA acumulen madurez operativa y adopción universal hacia el horizonte **2025–2033** marcado por CNSA 2.0, resultará razonable simplificar hacia **PQC puro** eliminando el componente clásico, transición que el Perfil B podrá ejecutar con menor urgencia regulatoria que el Perfil C.

---

## 6. Conclusiones y Referencias

La transición hacia la criptografía post-cuántica requiere combinar rigor criptográfico con ingeniería de sistemas: mientras los experimentos con `AerSimulator` muestran el comportamiento de algoritmos cuánticos básicos y su sensibilidad al ruido NISQ, el análisis de ciberseguridad evidencia que la amenaza cuántica sobre la infraestructura actual exige actuar desde hoy mediante inventarios criptográficos, agilidad criptográfica, despliegues híbridos en TLS 1.3 y adopción progresiva de los estándares **FIPS 203, FIPS 204 y FIPS 205**.

### Referencias (Formato APA)

- CISA, NSA, & NIST. (2023). *Quantum-readiness: Migration to post-quantum cryptography*. Cybersecurity and Infrastructure Security Agency. https://www.cisa.gov/resources-tools/resources/quantum-readiness-migration-post-quantum-cryptography
- ETSI. (2024). *Quantum-safe cryptography (QSC); Transition guidelines* (ETSI GR QSC 006). European Telecommunications Standards Institute. https://www.etsi.org/
- Kwiatkowski, K., Kampanakis, P., & Westerbaan, B. (2024). *Post-quantum hybrid ECDHE-MLKEM key agreement for TLSv1.3* (Internet-Draft draft-ietf-tls-ecdhe-mlkem). Internet Engineering Task Force (IETF). https://datatracker.ietf.org/doc/draft-ietf-tls-ecdhe-mlkem/
- National Institute of Standards and Technology. (2024a). *Module-lattice-based key-encapsulation mechanism standard* (Federal Information Processing Standards Publication 203). U.S. Department of Commerce. https://doi.org/10.6028/NIST.FIPS.203
- National Institute of Standards and Technology. (2024b). *Module-lattice-based digital signature standard* (Federal Information Processing Standards Publication 204). U.S. Department of Commerce. https://doi.org/10.6028/NIST.FIPS.204
- National Institute of Standards and Technology. (2024c). *Stateless hash-based digital signature standard* (Federal Information Processing Standards Publication 205). U.S. Department of Commerce. https://doi.org/10.6028/NIST.FIPS.205
- National Security Agency. (2022). *Announcing the Commercial National Security Algorithm Suite 2.0 (CNSA 2.0)* (Cybersecurity Advisory). U.S. Department of Defense. https://media.defense.gov/2022/Sep/07/2003071834/-1/-1/0/CSA_CNSA_2.0_ALGORITHMS_.PDF
- Paquin, C., Stebila, D., & Tamvada, G. (2020). Benchmarking post-quantum cryptography in TLS. En *Post-Quantum Cryptography: 11th International Conference, PQCrypto 2020* (pp. 72–91). Springer. https://doi.org/10.1007/978-3-030-44223-1_5
- Westerbaan, B., & Sullivan, N. (2023). *The state of the post-quantum Internet*. Cloudflare Blog. https://blog.cloudflare.com/post-quantum-for-all/
