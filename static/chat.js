// ======================================================
// ESTADO GLOBAL
// ======================================================
let conversaAtualId = null;
let tituloatual = null;

const chatdiv = document.querySelector(".chat");
const add = document.getElementById("add");
const rem = document.getElementById("rem");

// Esconde os botões no início
add.classList.add("hidden");
rem.classList.add("hidden");

// ======================================================
// WELCOME FIXO — NUNCA SERÁ DESTRUÍDO
// ======================================================
const varbemvindo = document.createElement("h1");
varbemvindo.id = "welcome";
varbemvindo.className = "welcome visible";
varbemvindo.innerHTML = "Seja Livre... Pergunte algo ao chat";
chatdiv.appendChild(varbemvindo);

// Controla aparecimento/desaparecimento
function bemvindo(state) {
    const w = document.getElementById("welcome");

    // Welcome aparece = true, Welcome some = false
    w.classList.toggle("hidden", !state);

    // Botões fazem o inverso
    add.classList.toggle("hidden", state);
    rem.classList.toggle("hidden", state);
}

bemvindo(true);

// ======================================================
// LOAD INICIAL
// ======================================================
window.onload = async function () {
    await carregarListaConversas();
    const mensagemInicial = getMensagemDaURL();

    if (mensagemInicial) {
        const input = document.querySelector(".msginput");
        input.value = mensagemInicial;

        await enviarMensagem();
    }
};

// ======================================================
// UTILIDADES
// ======================================================
function verificarEnter(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        enviarMensagem();
    }
}

function getMensagemDaURL() {
    const params = new URLSearchParams(window.location.search);
    return params.get("msg");
}

// ======================================================
// API: LISTAR CONVERSAS
// ======================================================
async function carregarListaConversas() {
    const response = await fetch('/conversas');
    const conversas = await response.json();

    const conversasDiv = document.querySelector('.history');
    conversasDiv.innerHTML = '';

    conversas.forEach(conversa => {
        const buttonHTML = document.createElement('button');
        buttonHTML.className = 'item-conversa';
        buttonHTML.id = `${conversa.conversa_id}`;

        if (conversa.conversa_id === conversaAtualId)
            buttonHTML.classList.add('active');

        buttonHTML.innerHTML = `${conversa.titulo}`;
        buttonHTML.onclick = () => carregarConversa(conversa.conversa_id);

        conversasDiv.appendChild(buttonHTML);
    });
}

// ======================================================
// API: NOVA CONVERSA
// ======================================================
async function criarNovaConversa() {
    const titulo = prompt("Nome da conversa:", "Novo Chat");
    if (!titulo) return;

    try {
        const response = await fetch('/conversas', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ titulo })
        });

        const novaConversa = await response.json();

        await carregarListaConversas();
        carregarConversa(novaConversa.conversa_id);

        tituloatual = titulo;
        bemvindo(false);
    } catch (error) {
        alert("Erro ao criar conversa");
        console.error(error);
    }
}

async function criarNovaConversaAuto(titulo = "💬 Nova Conversa") {
    const response = await fetch('/conversas', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ titulo })
    });

    const novaconversa = await response.json();
    conversaAtualId = novaconversa.conversa_id;

    window.history.replaceState({}, document.title, window.location.pathname);

    bemvindo(false);
    return novaconversa;
}

// ======================================================
// API: CARREGAR HISTÓRICO
// ======================================================
async function carregarConversa(id) {
    conversaAtualId = id;
    carregarListaConversas();

    // limpa mensagens e recoloca o welcome SEMPER
    chatdiv.replaceChildren();
    chatdiv.appendChild(varbemvindo); // <-- ESSA LINHA FALTAVA

    try {
        const response = await fetch(`/conversas/${id}/mensagens`);
        const mensagens = await response.json();

        mensagens.forEach(msg => {
            renderizarMensagem(msg.remetente.toLowerCase(), msg.conteudo);
        });

        rolarParaBaixo();
    } catch (error) {
        console.error("Erro ao carregar historico: ", error);
    }

    // welcome some automaticamente
    bemvindo(false); 
}

// ======================================================
// API: ENVIAR MENSAGEM
// ======================================================
async function enviarMensagem() {
    const input = document.querySelector(".msginput");
    const texto = input.value.trim();

    if (!texto) return;

    if (conversaAtualId == null) {
        await criarNovaConversaAuto();
    }

    renderizarMensagem('usuario', texto);
    input.value = '';
    rolarParaBaixo();

    try {
        const response = await fetch(`/conversas/${conversaAtualId}/mensagens`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ conteudo: texto })
        });

        if (!response.ok) throw new Error("Erro na API");

        const respostaIA = await response.json();

        renderizarMensagem('ia', respostaIA.conteudo);
        carregarListaConversas();
        rolarParaBaixo();

    } catch (error) {
        renderizarMensagem('ia', "⚠️ Erro ao comunicar com o servidor.");
        console.error(error);
    }
}

// ======================================================
// API: EXCLUIR CONVERSA
// ======================================================
async function excluirConversa() {
    if (!conversaAtualId) return;

    try {
        await fetch(`/conversas/${conversaAtualId}`, {
            method: "DELETE",
            headers: { "Content-Type": "application/json" }
        });

        carregarListaConversas();
        limparChat();
        bemvindo(true);
    } catch (error) {
        console.error(error);
    }
}

// ======================================================
// RENDERIZAÇÃO
// ======================================================
function renderizarMensagem(author, message) {
    const classCss = author === 'usuario' ? 'user' : 'ia';
    const conteudo = classCss === 'ia' ? marked.parse(message) : message;

    const html = `
        <div class="box-message-${classCss}">
            <div class="message-${classCss}">${conteudo}</div>
        </div>
    `;

    chatdiv.insertAdjacentHTML('beforeend', html);
}

function rolarParaBaixo() {
    chatdiv.scrollTop = chatdiv.scrollHeight;
}

// ======================================================
// LIMPEZA
// ======================================================
function limparMensagens() {
    chatdiv.replaceChildren();
    chatdiv.appendChild(varbemvindo);
}

function limparChat() {
    chatdiv.replaceChildren();      // limpa sem quebrar o DOM
    chatdiv.appendChild(varbemvindo);

    bemvindo(true);

    conversaAtualId = null;
    tituloatual = null;
}

// ======================================================
// DEV: RESETAR DB
// ======================================================
async function clearDB() {
    try {
        await fetch("/api/db", {
            method: "DELETE",
            headers: { "Content-Type": "application/json" }
        });
    } catch (error) {
        console.error(error);
    } finally {
        carregarListaConversas();
        limparChat();
    }
}
