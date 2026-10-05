import os
import pickle
import faiss
import streamlit as st

from src.embeddings import load_embedding_model
from src.retriever import retrieve_documents
from src.generator import generate_answer
from src.reranker import load_reranker
from src.document_manager import (
    add_pdf_to_vector_store,
    delete_document_from_vector_store
)
from src.document_registry import get_documents


# ============================================================
# CONFIGURATION
# ============================================================

INDEX_PATH = "vector_db/faiss.index"
CHUNKS_PATH = "vector_db/chunks.pkl"


# ============================================================
# STREAMLIT PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Local RAG Knowledge Assistant",
    page_icon="📚",
    layout="wide"
)


# ============================================================
# LOAD RAG SYSTEM
# ============================================================

@st.cache_resource
def load_rag_system():

    index = faiss.read_index(
        INDEX_PATH
    )

    with open(
        CHUNKS_PATH,
        "rb"
    ) as file:

        chunks = pickle.load(
            file
        )

    embedding_model = load_embedding_model()

    reranker = load_reranker()

    return (
        index,
        chunks,
        embedding_model,
        reranker
    )


# ============================================================
# HEADER
# ============================================================

st.title(
    "📚 Local RAG Knowledge Assistant"
)

st.markdown(
    """
    Ask questions about your documents and get
    **grounded answers with source citations**.
    """
)


# ============================================================
# LOAD RAG SYSTEM
# ============================================================

with st.spinner(
    "Loading RAG system..."
):

    index, chunks, embedding_model, reranker = (
        load_rag_system()
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    # --------------------------------------------------------
    # DOCUMENT UPLOAD
    # --------------------------------------------------------

    st.header(
        "📂 Documents"
    )

    uploaded_file = st.file_uploader(
        "Upload a PDF",
        type=["pdf"]
    )


    # --------------------------------------------------------
    # PROCESS UPLOADED PDF
    # --------------------------------------------------------

    if uploaded_file is not None:

        os.makedirs(
            "data/uploaded_pdfs",
            exist_ok=True
        )

        pdf_path = os.path.join(
            "data/uploaded_pdfs",
            uploaded_file.name
        )

        with open(
            pdf_path,
            "wb"
        ) as file:

            file.write(
                uploaded_file.getbuffer()
            )


        file_identifier = (
            uploaded_file.name,
            uploaded_file.size
        )


        if (
            st.session_state.get(
                "processed_file"
            )
            != file_identifier
        ):

            with st.spinner(
                "📄 Indexing document..."
            ):

                try:

                    stats = add_pdf_to_vector_store(
                        pdf_path,
                        embedding_model
                    )

                    st.session_state[
                        "processed_file"
                    ] = file_identifier

                    load_rag_system.clear()

                    st.success(
                        "PDF indexed successfully!"
                    )

                    st.write(
                        f"📄 Pages: "
                        f"{stats['pages']}"
                    )

                    st.write(
                        f"🧩 New chunks: "
                        f"{stats['chunks']}"
                    )

                    st.write(
                        f"📚 Total chunks: "
                        f"{stats['total_chunks']}"
                    )

                    st.write(
                        f"🔢 Total vectors: "
                        f"{stats['total_vectors']}"
                    )

                    st.rerun()

                except Exception as error:

                    st.error(
                        f"Indexing failed: {error}"
                    )


    # --------------------------------------------------------
    # CURRENT KNOWLEDGE BASE
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "📖 Current Knowledge Base"
    )

    documents = get_documents()


    if not documents:

        st.info(
            "No documents registered yet."
        )


    else:

        for document in documents:

            document_id = document[
                "document_id"
            ]

            filename = document[
                "filename"
            ]

            pages = document[
                "pages"
            ]

            chunks_count = document[
                "chunks"
            ]


            st.write(
                f"📄 **{filename}**"
            )

            st.caption(
                f"{pages} pages • "
                f"{chunks_count} chunks"
            )


            # ------------------------------------------------
            # DELETE BUTTON
            # ------------------------------------------------

            delete_key = (
                f"delete_{document_id}"
            )

            if st.button(
                "🗑️ Delete",
                key=delete_key,
                use_container_width=True
            ):

                st.session_state[
                    "document_to_delete"
                ] = document_id


    # --------------------------------------------------------
    # DELETE CONFIRMATION
    # --------------------------------------------------------

    if (
        "document_to_delete"
        in st.session_state
    ):

        document_id = st.session_state[
            "document_to_delete"
        ]

        document = next(
            (
                doc
                for doc in documents
                if doc["document_id"] == document_id
            ),
            None
        )


        if document is not None:

            st.warning(
                f"Delete **{document['filename']}**?"
            )

            col1, col2 = st.columns(2)


            with col1:

                if st.button(
                    "Yes, delete",
                    key="confirm_delete",
                    use_container_width=True
                ):

                    with st.spinner(
                        "🗑️ Deleting document..."
                    ):

                        try:

                            stats = (
                                delete_document_from_vector_store(
                                    document_id,
                                    embedding_model
                                )
                            )


                            # Clear cached RAG system
                            load_rag_system.clear()


                            # Remove pending deletion
                            del st.session_state[
                                "document_to_delete"
                            ]


                            st.success(
                                "Document deleted successfully!"
                            )


                            st.write(
                                f"🗑️ Deleted chunks: "
                                f"{stats['deleted_chunks']}"
                            )

                            st.write(
                                f"📚 Remaining chunks: "
                                f"{stats['remaining_chunks']}"
                            )

                            st.rerun()


                        except Exception as error:

                            st.error(
                                f"Deletion failed: {error}"
                            )


            with col2:

                if st.button(
                    "Cancel",
                    key="cancel_delete",
                    use_container_width=True
                ):

                    del st.session_state[
                        "document_to_delete"
                    ]

                    st.rerun()


    # --------------------------------------------------------
    # SYSTEM INFORMATION
    # --------------------------------------------------------

    st.divider()

    st.header(
        "⚙️ System"
    )

    st.write(
        "🧠 Embedding Model"
    )

    st.caption(
        "all-MiniLM-L6-v2"
    )

    st.write(
        "🔎 Vector Database"
    )

    st.caption(
        "FAISS"
    )

    st.write(
        "🤖 Local LLM"
    )

    st.caption(
        "Qwen 3 8B"
    )

    st.write(
        "🎯 Reranker"
    )

    st.caption(
        "MS MARCO MiniLM"
    )


    # --------------------------------------------------------
    # CONVERSATION CONTROLS
    # --------------------------------------------------------

    st.divider()

    st.header(
        "💬 Conversation"
    )

    if st.button(
        "🗑️ Clear Chat",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()


# ============================================================
# CHAT HISTORY
# ============================================================

if "messages" not in st.session_state:

    st.session_state.messages = []


for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# ============================================================
# CHAT INPUT
# ============================================================

question = st.chat_input(
    "Ask a question about your documents..."
)


# ============================================================
# PROCESS QUESTION
# ============================================================

if question:

    # --------------------------------------------------------
    # USER MESSAGE
    # --------------------------------------------------------

    with st.chat_message(
        "user"
    ):

        st.markdown(
            question
        )


    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )


    # --------------------------------------------------------
    # ASSISTANT
    # --------------------------------------------------------

    with st.chat_message(
        "assistant"
    ):

        # ====================================================
        # RETRIEVAL
        # ====================================================

        with st.spinner(
            "🔎 Searching documents..."
        ):

            results = retrieve_documents(
                question,
                embedding_model,
                index,
                chunks,
                reranker,
                candidate_k=8,
                final_k=3
            )


        # ====================================================
        # GENERATION
        # ====================================================

        with st.spinner(
            "🤖 Generating answer..."
        ):

            answer = generate_answer(
                question,
                results
            )


        # ====================================================
        # ANSWER
        # ====================================================

        st.markdown(
            answer
        )


        # ====================================================
        # SOURCES
        # ====================================================

        st.markdown(
            "### 📚 Sources"
        )


        for rank, result in enumerate(
            results,
            start=1
        ):

            section_name = result.get(
                "section",
                "Unknown section"
            )

            filename = result.get(
                "filename",
                os.path.basename(
                    result["source"]
                )
            )


            with st.expander(
                f"Source {rank} — {section_name}"
            ):

                st.write(
                    f"**Document:** "
                    f"{filename}"
                )

                st.write(
                    f"**Pages:** "
                    f"{result['pages']}"
                )

                st.write(
                    f"**FAISS similarity:** "
                    f"{result['score']:.4f}"
                )

                st.write(
                    f"**Reranker score:** "
                    f"{result['rerank_score']:.4f}"
                )

                st.write(
                    f"**Final score:** "
                    f"{result['final_score']:.4f}"
                )

                st.write(
                    f"**Source:** "
                    f"{result['source']}"
                )

                st.markdown(
                    "#### Retrieved Text"
                )

                st.write(
                    result["text"]
                )


    # --------------------------------------------------------
    # SAVE ASSISTANT MESSAGE
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )