
conversaAtualId = null;
tituloatual = null;

const buttonAdd = document.getElementById("add");
const buttonRemove = document.getElementById("remove")

buttonAdd.className = "hidden";
buttonRemove.className = "hidden";


function bemvindo() {
    const chatdiv = document.querySelector(".chat")
    const bemvindo = document.createElement("h1")
    bemvindo.id = "welcome"
    bemvindo.className = ""
    bemvindo.innerHTML = "Seja Livre... Pergunte algo ao chat"
    chatdiv.appendChild(bemvindo)
}

bemvindo();

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
        buttonHTML.id = `${conversa.conversa_id}`
        if (conversa.conversa_id === conversaAtualId) buttonHTML.classList.add('active')

        buttonHTML.innerHTML = `${conversa.titulo}`

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
        tituloatual = titulo;

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
    window.history.replaceState({}, document.title, window.location.pathname);
    tituloatual = titulo;

    const buttonAdd = document.getElementById("add");
    const buttonRemove = document.getElementById("remove")

    buttonAdd.className = "";
    buttonRemove.className = "";

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

        const buttonAdd = document.getElementById("add");
        const buttonRemove = document.getElementById("remove")
        bemvindo.className = "hidden"
        buttonAdd.className = "";
        buttonRemove.className = "";
        rolarParaBaixo();
    } catch (error) {
        console.error("Erro ao carregar historico: ", error);
    }
}

// ===================== API: ENVIAR MSG =========================

async function enviarMensagem() {
    let primeiramsg = "true";
    if (!conversaAtualId) {
        const novaconversa = await criarNovaConversaAuto();
        conversaAtualId = novaconversa.conversa_id;
        primeiramsg = "true";

        await carregarListaConversas();
        await carregarConversa(conversaAtualId);

    }

    if (tituloatual != "💬 Nova Conversa") {
        primeiramsg = "false";
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
            body: JSON.stringify({ "conteudo": texto, "primeiramsg": primeiramsg})
        });

        if (!response.ok) throw new Error("Erro na API");

        const respostaIA = await response.json();
        if (primeiramsg == "true") {
            definirTitulo(conversaAtualId, respostaIA.titulo)
        }

        renderizarMensagem('ia', respostaIA.conteudo);
        rolarParaBaixo();
    } catch (error) {
        renderizarMensagem('ia', "⚠️ Erro ao comunicar com o servidor.");
        console.error(error);
    }
}

function definirTitulo(id, titulo) {
    const buttonconversa = document.getElementById(id);

    buttonconversa.innerHTML = `💬` + `${titulo}`;
    tituloatual = titulo;
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
        conversaAtualId = null;
        tituloatual = null;
        const buttonAdd = document.getElementById("add");
        const buttonRemove = document.getElementById("remove")
        buttonAdd.className = "hidden";
        buttonRemove.className = "hidden";
        bemvindo();
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
    const buttonAdd = document.getElementById("add");
    const buttonRemove = document.getElementById("remove")

    buttonAdd.className = "hidden";
    buttonRemove.className = "hidden";
    bemvindo();
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