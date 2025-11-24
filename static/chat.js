
conversaAtualId = null;

window.onload = async function() {
    await carregarListaConversas();

    const mensagemInicial = getMensagemDaURL();

    if (mensagemInicial) {
        const input = document.querySelector(".msginput");
        input.value = mensagemInicial;

        await enviarMensagem();
    }
}

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

// ========= API: Listar Conversas ============

async function carregarListaConversas() {
    const response = await fetch('/conversas');
    const conversas = await response.json();

    const conversasDiv = document.querySelector('.history');
    conversasDiv.innerHTML = '';

    conversas.forEach(conversa => {
        const buttonHTML = document.createElement('button');
        buttonHTML.className = 'item-conversa';
        if (conversa.conversa_id === conversaAtualId) buttonHTML.classList.add('active')

        buttonHTML.innerHTML = `💬 ${conversa.titulo}`

        buttonHTML.onclick = () => carregarConversa(conversa.conversa_id);

        conversasDiv.appendChild(buttonHTML);
    });
}

// =================== API: Criar Nova Conversa ======================

async function criarNovaConversa() {
    const titulo = prompt("Nome da conversa:", "Novo Chat");
    if (!titulo) return;

    try {
        const response = await fetch('/conversas', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({titulo: titulo})
        });

        const novaConversa = await response.json();

        await carregarListaConversas();
        carregarConversa(novaConversa.conversa_id);
    } catch (error) {
        alert("Erro ao criar conversa");
        console.error(error);
    }
}

async function criarNovaConversaAuto(titulo = "Nova Conversa") {
    const response = await fetch('/conversas', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ titulo })
    });
    window.history.replaceState({}, document.title, window.location.pathname);
    return await response.json();
}

// ================ API: CarregarHistorico =================

async function carregarConversa(id) {
    conversaAtualId = id;

    carregarListaConversas();

    const chatDiv = document.querySelector('.chat');
    chatDiv.innerHTML = '';

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
}

// ===================== API: ENVIAR MSG =========================

async function enviarMensagem() {
    if (!conversaAtualId) {
        const novaconversa = await criarNovaConversaAuto();
        conversaAtualId = novaconversa.conversa_id;

        await carregarListaConversas();
        await carregarConversa(conversaAtualId);

    }
    const input = document.querySelector(".msginput");
    const texto = input.value.trim();

    if (!texto) return;

    renderizarMensagem('usuario', texto);
    input.value = '';
    rolarParaBaixo();

    try {
        const response = await fetch(`/conversas/${conversaAtualId}/mensagens`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ conteudo: texto})
        });

        if (!response.ok) throw new Error("Erro na API");

        const respostaIA = await response.json();

        renderizarMensagem('ia', respostaIA.conteudo);
        rolarParaBaixo();
    } catch (error) {
        renderizarMensagem('ia', "⚠️ Erro ao comunicar com o servidor.");
        console.error(error);
    }
}

// =========== API: EXCLUIR CONVERSAS ================

async function excluirConversa() {
    
    try {
        const response = await fetch(`/conversas/${conversaAtualId}`, {
            method: "DELETE",
            headers: { "Content-Type": "application/json" }
        });

        console.log(response);
        carregarListaConversas();
        const chatDiv = document.querySelector(".chat");
        chatDiv.innerHTML = '';
        
    } catch (error) {
        console.error(error);
    }
}

function renderizarMensagem(author, message) {
    const chatbox = document.querySelector(".chat");

    const classCss = author === 'usuario' ? 'user' : 'ia';

    if (classCss == 'ia') {
        conteudo = marked.parse(message);
    } else {
        conteudo = message;
    }

    const html = `
        <div class="box-message-${classCss}">
            <div class="message-${classCss}">${conteudo}</div>
        </div>
    `;
    
    chatbox.insertAdjacentHTML('beforeend', html);
}

function rolarParaBaixo() {
    const chatDiv = document.querySelector('.chat');
    chatDiv.scrollTop = chatDiv.scrollHeight;
}

function limparChat() {
    const chatdiv = document.querySelector(".chat");
    chatdiv.innerHTML = "";
}

// ========== Funções para ambiente de desenvolvimento ========

async function clearDB() {
    try {
        const response = await fetch("/api/db", {
            method: "DELETE",
            headers: { "Content-Type": "application/json" }
        });

        console.log(response);
        
    } catch (error) {
        console.error(error);
    } finally {
        carregarListaConversas();
        limparChat();
    }

}