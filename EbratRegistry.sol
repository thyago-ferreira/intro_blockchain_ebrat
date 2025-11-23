// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract EbratRegistry {
    struct Documento {
        uint256 timestamp;
        address emissor;
        bool existe;
    }

    mapping(bytes32 => Documento) public documentos;
    
    // Evento para avisar que um novo eBRAT foi registrado
    event DocumentoRegistrado(bytes32 indexed hash, address indexed emissor);

    function registrarDocumento(bytes32 _hash) public {
        require(!documentos[_hash].existe, "Erro: Documento ja registrado.");
        documentos[_hash] = Documento(block.timestamp, msg.sender, true);
        emit DocumentoRegistrado(_hash, msg.sender);
    }

    function verificarDocumento(bytes32 _hash) public view returns (bool, uint256, address) {
        return (documentos[_hash].existe, documentos[_hash].timestamp, documentos[_hash].emissor);
    }
}
