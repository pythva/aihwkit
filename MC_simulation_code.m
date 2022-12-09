
    % writting the code based on http://www.cchem.berkeley.edu/chem195/index.html
    % file: http://www.cchem.berkeley.edu/chem195/_l_j___n_v_t_8m.html#a9dcf63ca6efe995fdc676be9ef33aa3e
    % Set configuration parameters

    function [coords, L] = init2DGrid(nPart,density)
    
        % Initialize with zeroes
        coords = zeros(2,nPart);
    
        % Get the cooresponding box size
        L = (nPart/density)^(1.0/2);
    
        % Find the lowest perfect square greater than or equal to the number of
        % particles
        nCube = 2;
        
        while (nCube^2 < nPart)
            nCube = nCube + 1;
        end
        
        
        % Start positioning - use a 3D index for counting the spots
        index = [0,0]';
        
        % Assign particle positions
        for part=1:nPart
            % Set coordinate
            coords(:,part) = (index+[0.5,0.5]')*(L/nCube);
            
            % Advance the index
            index(1) = index(1) + 1;
            if (index(1) == nCube) 
                index(1) = 0;
                index(2) = index(2) + 1;
                if (index(2) == nCube)
                    index(2) = 0;
                end
            end
        end
    
    end



    nPart = 100;        % Number of particles
    density = 0.85;     % Density of particles
    
    % Set simulation parameters
    Temp = 2.0;         % Simulation temperature
    beta = 1.0/Temp;    % Inverse temperature
    maxDr = 0.1;        % Maximal displacement
    
    nSteps = 10000;     % Total simulation time (in integration steps)
    printFreq = 100;    % Printing frequency
    
    % Set initial configuration
    [coords L] = init2DGrid(nPart,density);
    
    % Calculate initial energy
    energy = LJ_Energy(coords,L);
    
    
    % ==============
    % MC Simulation
    % ==============
    for step = 1:nSteps
        
        if (mod(step,printFreq)==0)
            step
        end
        
        % each MC step involves suggesting nPart trial moves 
        
        for i=1:nPart
            % Suggest a trial move for particle i
            rTrial = coords(:,i) + maxDr*(rand(3,1)-0.5);
                
            % Apply periodic boundary conditions
            rTrial = PBC(rTrial,L);
          
            % Calculate the change in energy due to this trial move
            deltaE = LJ_EnergyChange(coords,rTrial,i,L);
    
            if (rand < exp(-beta*deltaE))
                % Accept displacement move
                coords(:,i) = rTrial;       % Update positions
                energy = energy + deltaE;   % Update energy
            end
        end
        
    end
    