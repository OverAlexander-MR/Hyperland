return {
  {
    "neovim/nvim-lspconfig",
    opts = {
      servers = {
        pylsp = {
          settings = {
            pylsp = {
              plugins = {
                --"line too long"
                pycodestyle = {
                  enabled = true,
                  maxLineLength = 200,
                  ignore = { "E501", "E203" },
                },
                -- Desactivar flake8
                flake8 = {
                  enabled = false,
                },
                -- Ruff
                ruff = {
                  enabled = false,
                },
              },
            },
          },
        },
      },
    },
  },
}
